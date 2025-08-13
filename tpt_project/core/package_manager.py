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
from ..handlers.deb_xz_handler import DebXzHandler
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
from ..handlers.powershell_handler import PowershellHandler
from ..handlers.nemas_patch_zip_handler import NemasPatchZipHandler
from ..handlers.meta_zip_handler import MetaZipHandler

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
            ".deb.xz": DebXzHandler,
            ".sh": ScriptHandler,
            ".py": ScriptHandler,
            ".AppImage": AppImageHandler,
            ".tar.gz": ArchiveHandler,
            ".tgz": ArchiveHandler,
            ".tar.xz": ArchiveHandler,
            ".rpm": RpmHandler,
            ".ps1": PowershellHandler,
            ".exe": ExeHandler,
            ".msi": MsiHandler,
            ".apk": AndroidApkHandler, # Por defecto, .apk es para Android

            # Formatos basados en metadatos (clave 'format' en el manifiesto)
            "flatpak": FlatpakHandler,
            "snap": SnapHandler,
            "alpine_apk": AlpineApkHandler,
            "android_apk": AndroidApkHandler, # Explícito para Android
            "nemas_patch_zip": NemasPatchZipHandler,
            "meta_zip": MetaZipHandler,
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
                if download_url.endswith(".deb.xz"):
                    pkg_format = ".deb.xz"
                elif download_url.endswith(".tar.gz"):
                    pkg_format = ".tar.gz"
                elif download_url.endswith(".tar.xz"):
                    pkg_format = ".tar.xz"
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
        else:
            self.logger.info("Este paquete no requiere descarga directa (ej. flatpak, snap).")

        # Llamar a la lógica de instalación subyacente
        self._perform_installation(package_info, temp_path)

    def _perform_installation(self, package_info: dict, file_path: Path | None):
        """Lógica de instalación que opera sobre un paquete ya descargado (o sin descarga)."""

        # 1. Verificar checksum si el archivo existe
        if file_path and "sha256" in package_info:
            self._verify_checksum(file_path, package_info["sha256"])

        # 2. Obtener e instanciar el manejador
        HandlerClass = self._get_handler_class(package_info)
        handler = HandlerClass(self, package_info, self.config, self.logger, temp_path=file_path)

        # 3. Instalar
        installation_details = handler.install()

        # 4. Guardar en la base de datos
        db = self._load_db()
        package_name = package_info['name']
        db[package_name] = {
            "version": package_info.get("version", "0.0.0"),
            "repository_url": package_info.get("repository_url"),
            "installation_details": installation_details
        }
        self._save_db(db)

        # 5. Limpiar el archivo descargado
        if file_path:
            file_path.unlink(missing_ok=True)

        self.logger.success(f"¡Paquete '{package_name}' instalado con éxito!")

    def install_from_staged_file(self, package_name: str, staged_filename: str | None):
        """Instala un paquete desde la zona de espera de AADPO."""
        self.logger.info(f"Instalando paquete preparado [bold magenta]{package_name}[/bold magenta] desde AADPO...")

        search_results = self.search(package_name)
        if not search_results:
            raise PackageNotFoundError(f"No se encontró información del paquete '{package_name}' en los repositorios para la instalación preparada.")
        package_info = search_results[0]

        staged_file_path = None
        if staged_filename:
            staged_file_path = self.config.DIR_STAGING / "files" / staged_filename
            if not staged_file_path.exists():
                raise TPTError(f"El archivo preparado '{staged_filename}' no se encuentra en la zona de espera.")

        # Llamar a la lógica de instalación, pasándole la ruta al archivo preparado
        self._perform_installation(package_info, staged_file_path)

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
        handler = HandlerClass(self, package_info_for_uninstall, self.config, self.logger)

        handler.uninstall(installation_details)

        # Eliminar de la base de datos
        del db[package_name]
        self._save_db(db)
        self.logger.success(f"¡Paquete '{package_name}' desinstalado con éxito!")

    def list_installed(self) -> dict:
        """Devuelve un diccionario de los paquetes instalados."""
        return self._load_db()

    def upgrade(self, no_apply: bool = False):
        """
        Descubre y aplica (o prepara) actualizaciones para TPT y el sistema.
        """
        self.logger.info("[bold blue]Iniciando proceso de actualización de TPT...[/bold blue]")

        # --- 1. Descubrir actualizaciones ---
        self.logger.info("\n[bold]Paso 1: Buscando actualizaciones disponibles[/bold]")
        tpt_updates = self._find_tpt_updates()
        system_updates = self._find_system_updates()

        if not tpt_updates and not any(system_updates.values()):
            self.logger.success("\n¡Todo está ya actualizado!")
            return

        # --- 2. Aplicar o preparar ---
        if no_apply:
            self.logger.info("\n[bold]Paso 2: Preparando actualizaciones para AADPO (sin aplicar)[/bold]")
            self._stage_updates(tpt_updates, system_updates)
        else:
            self.logger.info("\n[bold]Paso 2: Aplicando actualizaciones directamente[/bold]")
            self._apply_system_updates_sources()
            self._apply_tpt_updates(tpt_updates)
            self._apply_system_package_updates(system_updates)
            # self._apply_patches() # Placeholder

        self.logger.success("\n[bold green]¡Proceso de actualización de TPT completado![/bold green]")

    def _find_tpt_updates(self) -> list[dict]:
        """Busca actualizaciones para los paquetes instalados por TPT."""
        self.logger.info("Buscando actualizaciones para paquetes de TPT...")
        installed_packages = self._load_db()
        packages_to_upgrade = []
        if not installed_packages:
            return []

        for name, details in installed_packages.items():
            installed_version_str = details.get("version", "0.0.0")
            try:
                search_results = self.search(name)
                if not search_results: continue

                latest_info = search_results[0]
                latest_version_str = latest_info.get("version", "0.0.0")
                if parse_version(latest_version_str) > parse_version(installed_version_str):
                    self.logger.info(f"[green]  - Actualización para [magenta]{name}[/magenta]: v{installed_version_str} -> v{latest_version_str}[/green]")
                    packages_to_upgrade.append(latest_info)
            except Exception as e:
                self.logger.error(f"No se pudo comprobar la actualización para '{name}': {e}")
        return packages_to_upgrade

    def _find_system_updates(self) -> dict:
        """Comprueba qué gestores de paquetes del sistema están disponibles."""
        self.logger.info("Detectando gestores de paquetes del sistema...")
        updates = {
            "apt": system.check_dependency("apt"),
            "flatpak": system.check_dependency("flatpak"),
            "snap": system.check_dependency("snap")
        }
        self.logger.info(f"Gestores detectados: {[k for k, v in updates.items() if v]}")
        return updates

    def _stage_updates(self, tpt_updates: list[dict], system_updates: dict):
        """Prepara las actualizaciones para ser aplicadas por AADPO."""
        staging_dir = self.config.DIR_STAGING
        staging_files_dir = staging_dir / "files"
        staging_files_dir.mkdir(exist_ok=True, parents=True)

        actions = []

        # Preparar actualizaciones de TPT
        for pkg_info in tpt_updates:
            action = {"action": "install_tpt", "name": pkg_info["name"]}
            if "download_url" in pkg_info:
                url = pkg_info["download_url"]
                filename = Path(url).name
                dest_path = staging_files_dir / filename
                self.logger.info(f"Descargando {filename} para preparación...")
                downloader.download_file(url, dest_path, self.logger)
                action["file"] = str(filename) # Guardar nombre relativo
            actions.append(action)

        # Preparar actualizaciones del sistema
        for manager, available in system_updates.items():
            if available:
                actions.append({"action": "sys_update", "manager": manager})

        # Guardar el manifiesto de AADPO
        manifest_path = staging_dir / "aadpo_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({"actions": actions}, f, indent=4)

        self.logger.success(f"Actualizaciones preparadas en {staging_dir}. Se aplicarán en el próximo reinicio/apagado si AADPO está integrado.")

    def _apply_tpt_updates(self, tpt_updates: list[dict]):
        """Aplica las actualizaciones de los paquetes de TPT."""
        if not tpt_updates:
            self.logger.info("No hay paquetes de TPT para actualizar.")
            return

        self.logger.info(f"Se actualizarán los siguientes paquetes de TPT: {[p['name'] for p in tpt_updates]}")
        for pkg_info in tpt_updates:
            try:
                self.install(pkg_info['name'])
            except Exception as e:
                self.logger.error(f"Falló la actualización de '{pkg_info['name']}': {e}")

    def _apply_system_updates_sources(self):
        """Actualiza las fuentes de los gestores de paquetes (ej. apt update)."""
        if system.check_dependency("apt"):
            try:
                self.logger.info("Ejecutando 'apt update'...")
                system.execute_command(["apt", "update"], self.logger, as_root=True)
            except TPTError as e:
                self.logger.error(f"Falló 'apt update': {e}")

    def _apply_system_package_updates(self, system_updates: dict):
        """Ejecuta los comandos de actualización para los gestores de paquetes del sistema."""
        self.logger.info("Actualizando paquetes del sistema...")
        if system_updates.get("apt"):
            try:
                self.logger.info("Ejecutando 'apt-get upgrade'...")
                system.execute_command(["apt-get", "upgrade", "-y"], self.logger, as_root=True)
                system.execute_command(["apt-get", "autoclean", "-y"], self.logger, as_root=True)
            except TPTError as e: self.logger.error(f"Falló la actualización de APT: {e}")

        if system_updates.get("flatpak"):
            try:
                self.logger.info("Ejecutando 'flatpak update'...")
                system.execute_command(["flatpak", "update", "-y"], self.logger)
            except TPTError as e: self.logger.error(f"Falló la actualización de Flatpak: {e}")

        if system_updates.get("snap"):
            try:
                self.logger.info("Ejecutando 'snap refresh'...")
                system.execute_command(["snap", "refresh"], self.logger, as_root=True)
            except TPTError as e: self.logger.error(f"Falló la actualización de Snap: {e}")

    def system_integrate_install(self):
        """Crea e instala un servicio de systemd para AADPO."""
        self.logger.info("Integrando AADPO con systemd...")
        if not system.check_dependency("systemctl"):
            raise CriticalTPTError("No se encontró 'systemctl'. No se puede integrar con el sistema.")

        # Obtener la ruta absoluta del script que se va a ejecutar
        # Asumimos que tpt-apply-updates está en el mismo directorio que tpt
        tpt_script_path = Path(sys.argv[0]).resolve()
        apply_script_path = tpt_script_path.parent / "tpt-apply-updates"

        if not apply_script_path.exists():
            raise CriticalTPTError(f"No se encuentra el script '{apply_script_path}'. No se puede crear el servicio.")

        service_name = "tpt-aadpo.service"
        service_path = Path(f"/etc/systemd/system/{service_name}")

        service_content = f"""[Unit]
Description=TPT - Aplicar actualizaciones pendientes en el apagado/reinicio
Documentation=https://github.com/tovicito/TPT
DefaultDependencies=no
Before=shutdown.target reboot.target halt.target kexec.target

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/bin/true
ExecStop={apply_script_path}
TimeoutStopSec=900s

[Install]
WantedBy=shutdown.target reboot.target halt.target kexec.target
"""
        self.logger.info(f"Creando fichero de servicio en {service_path}")
        try:
            # Usamos tee para escribir el fichero como root
            command = ["tee", str(service_path)]
            system.execute_command(command, self.logger, as_root=True, input=service_content)

            self.logger.info("Recargando demonio de systemd...")
            system.execute_command(["systemctl", "daemon-reload"], self.logger, as_root=True)

            self.logger.info(f"Activando servicio '{service_name}'...")
            system.execute_command(["systemctl", "enable", service_name], self.logger, as_root=True)

            self.logger.success("¡Servicio AADPO instalado y activado con éxito!")
            self.logger.info("Las actualizaciones preparadas con 'tpt upgrade --no-apply' se instalarán al apagar o reiniciar.")
        except TPTError as e:
            raise TPTError(f"Falló la instalación del servicio de systemd: {e}")

    def system_integrate_uninstall(self):
        """Desinstala el servicio de systemd para AADPO."""
        self.logger.info("Desinstalando el servicio AADPO de systemd...")
        if not system.check_dependency("systemctl"):
            raise CriticalTPTError("No se encontró 'systemctl'. No se puede desinstalar el servicio.")

        service_name = "tpt-aadpo.service"
        service_path = Path(f"/etc/systemd/system/{service_name}")

        try:
            if service_path.exists():
                self.logger.info(f"Desactivando servicio '{service_name}'...")
                system.execute_command(["systemctl", "disable", service_name], self.logger, as_root=True)

                self.logger.info(f"Eliminando fichero de servicio {service_path}...")
                system.execute_command(["rm", "-f", str(service_path)], self.logger, as_root=True)

                self.logger.info("Recargando demonio de systemd...")
                system.execute_command(["systemctl", "daemon-reload"], self.logger, as_root=True)

                self.logger.success("¡Servicio AADPO desinstalado con éxito!")
            else:
                self.logger.warning("El servicio AADPO no parece estar instalado.")
        except TPTError as e:
            raise TPTError(f"Falló la desinstalación del servicio de systemd: {e}")
