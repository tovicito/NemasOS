import json
import hashlib
import requests
from pathlib import Path

from packaging.version import parse as parse_version

from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils import downloader, system
from ..utils.exceptions import *

# Importar todos los manejadores disponibles
from ..handlers.base_handler import BaseHandler
from ..handlers.deb_handler import DebHandler
from ..handlers.script_handler import ScriptHandler
from ..handlers.appimage_handler import AppImageHandler
from ..handlers.archive_handler import ArchiveHandler
from ..handlers.flatpak_handler import FlatpakHandler
from ..handlers.snap_handler import SnapHandler
from ..handlers.rpm_handler import RpmHandler
from ..handlers.exe_handler import ExeHandler
from ..handlers.msi_handler import MsiHandler
from ..handlers.alpine_apk_handler import AlpineApkHandler
from ..handlers.android_apk_handler import AndroidApkHandler

class PackageManager:
    """
    Clase central que orquesta la búsqueda, instalación, desinstalación y actualización de paquetes.
    """
    def __init__(self, config: Configuracion, logger: Logger):
        self.config = config
        self.logger = logger
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": f"TPT-PackageManager/3.0"})
        self.progress_callback = None # Para la GUI

        self.handler_map = {
            # Formatos basados en extensión de archivo
            ".deb": DebHandler,
            ".sh": ScriptHandler,
            ".py": ScriptHandler,
            ".AppImage": AppImageHandler,
            ".tar.gz": ArchiveHandler,
            ".tgz": ArchiveHandler,
            ".rpm": RpmHandler,
            ".exe": ExeHandler,
            ".msi": MsiHandler,
            ".apk": AndroidApkHandler, # Por defecto, .apk es para Android

            # Formatos basados en metadatos (clave 'format' en el manifiesto)
            "flatpak": FlatpakHandler,
            "snap": SnapHandler,
            "alpine_apk": AlpineApkHandler,
            "android_apk": AndroidApkHandler, # Explícito para Android
        }

    def _get_handler_class(self, package_info: dict) -> type[BaseHandler]:
        """Determina qué clase de manejador usar para un paquete."""
        # Priorizamos el formato explícito en los metadatos
        pkg_format = package_info.get("format")

        # Si no hay formato explícito, intentamos inferir por la extensión
        if not pkg_format:
            download_url = package_info.get("download_url")
            if download_url:
                # Manejar extensiones compuestas como .tar.gz
                if download_url.endswith(".tar.gz"):
                    pkg_format = ".tar.gz"
                else:
                    pkg_format = Path(download_url).suffix
            else:
                raise UnsupportedFormatError("No se puede determinar el formato: el paquete no tiene 'format' ni 'download_url'.")

        if not pkg_format:
            raise UnsupportedFormatError("No se pudo determinar el formato del paquete desde la URL o los metadatos.")

        handler_class = self.handler_map.get(pkg_format)
        if not handler_class:
            raise UnsupportedFormatError(f"El formato de paquete '{pkg_format}' no es compatible.")

        self.logger.info(f"Usando manejador: [bold yellow]{handler_class.__name__}[/bold yellow]")
        return handler_class

    def _load_db(self) -> dict:
        """Carga la base de datos de paquetes instalados."""
        if not self.config.BD_PAQUETES_INSTALADOS.exists():
            return {}
        try:
            with open(self.config.BD_PAQUETES_INSTALADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"No se pudo leer la base de datos de paquetes. Creando una nueva. Error: {e}")
            return {}

    def _save_db(self, db: dict):
        """Guarda la base de datos de paquetes instalados."""
        try:
            with open(self.config.BD_PAQUETES_INSTALADOS, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
        except IOError as e:
            raise CriticalTPTError(f"No se pudo escribir en la base de datos de paquetes: {e}")

    def _verify_checksum(self, file_path: Path, expected_sha256: str):
        """Verifica el checksum SHA256 de un archivo."""
        self.logger.info("Verificando suma de comprobación (checksum)...")
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)

            calculated_sha256 = sha256.hexdigest()
            if calculated_sha256 == expected_sha256:
                self.logger.success("Suma de comprobación verificada correctamente.")
            else:
                raise VerificationError(f"¡Suma de comprobación no coincide! Esperado: {expected_sha256}, Calculado: {calculated_sha256}. El archivo puede estar corrupto o manipulado.")
        except IOError as e:
            raise VerificationError(f"No se pudo leer el archivo para verificar el checksum: {e}")

    def _get_repo_urls(self) -> list[str]:
        """Lee las URLs de los repositorios desde el fichero de configuración."""
        if not self.config.ARCHIVO_REPOS.exists():
            self.logger.info("Archivo de repositorios no encontrado. Creando uno con los valores por defecto.")
            self.config.ARCHIVO_REPOS.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.ARCHIVO_REPOS, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.config.REPOS_POR_DEFECTO) + "\n")
            return self.config.REPOS_POR_DEFECTO

        with open(self.config.ARCHIVO_REPOS, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    def _fetch_manifest(self, repo_url: str) -> dict | None:
        """Descarga y cachea el manifiesto (packages.json) de un repositorio."""
        manifest_url = repo_url.rstrip('/') + "/" + self.config.ARCHIVO_MANIFIESTO_REPO
        cache_path = self.config.DIR_CACHE_REPOS / hashlib.sha256(manifest_url.encode()).hexdigest()

        try:
            self.logger.debug(f"Buscando manifiesto en {manifest_url}")
            response = self._session.get(manifest_url, timeout=15)
            response.raise_for_status()
            manifest_data = response.json()
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f)
            return manifest_data
        except (requests.RequestException, json.JSONDecodeError) as e:
            self.logger.warning(f"No se pudo obtener el manifiesto de {repo_url}: {e}")
            if cache_path.exists():
                self.logger.info(f"Usando manifiesto cacheado para {repo_url}.")
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None

    def search(self, term: str) -> list[dict]:
        """Busca un término en todos los repositorios configurados."""
        found_packages = []
        repo_urls = self._get_repo_urls()

        for repo_url in repo_urls:
            manifest = self._fetch_manifest(repo_url)
            if not manifest or 'packages' not in manifest:
                continue

            for pkg_name, pkg_details in manifest['packages'].items():
                # Buscar en el nombre, descripción y palabras clave
                search_fields = [
                    pkg_name,
                    pkg_details.get('description', ''),
                    ' '.join(pkg_details.get('keywords', []))
                ]
                if any(term.lower() in field.lower() for field in search_fields):
                    # Añadir información clave al diccionario del paquete
                    pkg_details['name'] = pkg_name
                    pkg_details['repository_url'] = repo_url
                    found_packages.append(pkg_details)

        return found_packages

    def install(self, package_name: str):
        """Busca, descarga (si es necesario) e instala un paquete."""
        self.logger.info(f"Iniciando instalación de [bold magenta]{package_name}[/bold magenta]...")

        # 1. Buscar el paquete
        search_results = self.search(package_name)
        if not search_results:
            raise PackageNotFoundError(f"Paquete '{package_name}' no encontrado.")

        if len(search_results) > 1:
            self.logger.warning(f"Múltiples paquetes encontrados para '{package_name}'. Se instalará el primero: '{search_results[0]['name']}'.")

        package_info = search_results[0]
        self.logger.info(f"Paquete encontrado: '{package_info['name']}' v{package_info.get('version', 'N/A')} en {package_info['repository_url']}")

        temp_path = None
        # 2. Descargar el paquete (si tiene una URL de descarga)
        if "download_url" in package_info:
            download_url = package_info["download_url"]
            file_name = Path(download_url).name
            temp_path = self.config.DIR_CACHE / "downloads" / file_name
            downloader.download_file(download_url, temp_path, self.logger)

            # 3. Verificar checksum
            if "sha256" in package_info:
                self._verify_checksum(temp_path, package_info["sha256"])
        else:
            self.logger.info("Este paquete no requiere descarga directa (ej. flatpak, snap).")

        # 4. Obtener e instanciar el manejador
        HandlerClass = self._get_handler_class(package_info)
        # Pasamos temp_path, que puede ser None
        handler = HandlerClass(package_info, self.config, self.logger, temp_path=temp_path)

        # 5. Instalar
        installation_details = handler.install()

        # 6. Guardar en la base de datos
        db = self._load_db()
        db[package_name] = {
            "version": package_info.get("version", "0.0.0"),
            "repository_url": package_info.get("repository_url"),
            "installation_details": installation_details
        }
        self._save_db(db)

        # 7. Limpiar
        temp_path.unlink(missing_ok=True)
        self.logger.success(f"¡Paquete '{package_name}' instalado con éxito!")

    def uninstall(self, package_name: str):
        self.logger.info(f"Desinstalando [bold magenta]{package_name}[/bold magenta]...")
        db = self._load_db()
        if package_name not in db:
            raise PackageNotFoundError(f"El paquete '{package_name}' no está instalado o no fue instalado por TPT.")

        package_data = db[package_name]
        installation_details = package_data.get("installation_details", {})
        handler_name = installation_details.get("handler")

        if not handler_name:
            raise TPTError("No se puede desinstalar: no se encontró el nombre del manejador en la base de datos.")

        # Encontrar la clase del manejador a partir de su nombre
        HandlerClass = next((cls for cls in self.handler_map.values() if cls.__name__ == handler_name), None)

        if not HandlerClass:
            raise UnsupportedFormatError(f"El manejador '{handler_name}' necesario para la desinstalación no se encuentra.")

        # Necesitamos la información del paquete original para la desinstalación
        package_info_for_uninstall = {"name": package_name}
        handler = HandlerClass(package_info_for_uninstall, self.config, self.logger)

        handler.uninstall(installation_details)

        # Eliminar de la base de datos
        del db[package_name]
        self._save_db(db)
        self.logger.success(f"¡Paquete '{package_name}' desinstalado con éxito!")

    def list_installed(self) -> dict:
        """Devuelve un diccionario de los paquetes instalados."""
        return self._load_db()

    def upgrade(self):
        """
        Ejecuta una actualización completa del sistema y de los paquetes de TPT.
        """
        self.logger.info("[bold blue]Iniciando proceso de actualización total de TPT...[/bold blue]")

        # --- 1. Actualización de los gestores de paquetes del sistema ---
        self.logger.info("\n[bold]Paso 1: Actualizando fuentes de los gestores de paquetes del sistema[/bold]")
        if system.check_dependency("apt"):
            try:
                self.logger.info("Ejecutando 'apt update'...")
                system.execute_command(["apt", "update"], self.logger, as_root=True)
                self.logger.success("'apt update' completado.")
            except TPTError as e:
                self.logger.error(f"Falló 'apt update': {e}")
        else:
            self.logger.info("'apt' no encontrado, omitiendo.")

        # --- 2. Actualización de paquetes de TPT ---
        self.logger.info("\n[bold]Paso 2: Buscando actualizaciones para los paquetes instalados por TPT[/bold]")
        installed_packages = self._load_db()
        packages_to_upgrade = []

        if not installed_packages:
            self.logger.info("No hay paquetes instalados por TPT para actualizar.")
        else:
            for name, details in installed_packages.items():
                installed_version_str = details.get("version", "0.0.0")
                self.logger.info(f"Comprobando [magenta]{name}[/magenta] (instalada: v{installed_version_str})...")

                try:
                    search_results = self.search(name)
                    if not search_results:
                        self.logger.warning(f"No se encontró '{name}' en los repositorios, no se puede actualizar.")
                        continue

                    latest_info = search_results[0]
                    latest_version_str = latest_info.get("version", "0.0.0")

                    installed_v = parse_version(installed_version_str)
                    latest_v = parse_version(latest_version_str)

                    if latest_v > installed_v:
                        self.logger.info(f"[bold green]¡Actualización encontrada para {name}! v{installed_version_str} -> v{latest_version_str}[/bold green]")
                        packages_to_upgrade.append(name)
                    else:
                        self.logger.info("Ya está en la última versión.")

                except Exception as e:
                    self.logger.error(f"No se pudo comprobar la actualización para '{name}': {e}")

        if packages_to_upgrade:
            self.logger.info(f"\n[bold]Se actualizarán los siguientes paquetes de TPT: {', '.join(packages_to_upgrade)}[/bold]")
            for pkg_name in packages_to_upgrade:
                try:
                    self.install(pkg_name)
                except Exception as e:
                    self.logger.error(f"Falló la actualización de '{pkg_name}': {e}")
        else:
            self.logger.success("Todos los paquetes de TPT están actualizados.")

        # --- 3. Aplicación de parches (Placeholder) ---
        self.logger.info("\n[bold]Paso 3: Buscando parches del sistema (funcionalidad pendiente)[/bold]")
        # self._apply_patches()

        # --- 4. Actualización final de paquetes del sistema ---
        self.logger.info("\n[bold]Paso 4: Actualizando paquetes del sistema (apt, flatpak, snap)[/bold]")

        # APT
        if system.check_dependency("apt-get"):
            try:
                self.logger.info("Ejecutando 'apt-get upgrade'...")
                system.execute_command(["apt-get", "upgrade", "-y"], self.logger, as_root=True)
                self.logger.info("Ejecutando 'apt-get autoclean'...")
                system.execute_command(["apt-get", "autoclean", "-y"], self.logger, as_root=True)
                self.logger.success("Actualización de APT completada.")
            except TPTError as e:
                self.logger.error(f"Falló la actualización de APT: {e}")

        # Flatpak
        if system.check_dependency("flatpak"):
            try:
                self.logger.info("Ejecutando 'flatpak update'...")
                system.execute_command(["flatpak", "update", "-y"], self.logger, as_root=False)
                self.logger.success("Actualización de Flatpak completada.")
            except TPTError as e:
                self.logger.error(f"Falló la actualización de Flatpak: {e}")

        # Snap
        if system.check_dependency("snap"):
            try:
                self.logger.info("Ejecutando 'snap refresh'...")
                system.execute_command(["snap", "refresh"], self.logger, as_root=True)
                self.logger.success("Actualización de Snap completada.")
            except TPTError as e:
                self.logger.error(f"Falló la actualización de Snap: {e}")

        self.logger.success("\n[bold green]¡Proceso de actualización total de TPT completado![/bold green]")
