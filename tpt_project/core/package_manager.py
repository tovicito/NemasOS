import json
import hashlib
import requests
import os
from pathlib import Path

from packaging.version import parse as parse_version

from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils import downloader, system
from ..utils.exceptions import *
from ..utils.i18n import _

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
        self.settings = self.config.load_settings()

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": f"TPT-PackageManager/5.0"})
        self._session.timeout = self.settings.get("network_timeout", 15)
        self._session.verify = self.settings.get("ssl_verify", True)

        self.progress_callback = None

        self.handler_map = {
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
            ".apk": AndroidApkHandler,
            "flatpak": FlatpakHandler,
            "snap": SnapHandler,
            "alpine_apk": AlpineApkHandler,
            "android_apk": AndroidApkHandler,
            "nemas_patch_zip": NemasPatchZipHandler,
            "meta_zip": MetaZipHandler,
        }

    def _get_handler_class(self, package_info: dict) -> type[BaseHandler]:
        pkg_format = package_info.get("format")
        if not pkg_format:
            download_url = package_info.get("download_url")
            if download_url:
                if download_url.endswith(".deb.xz"): pkg_format = ".deb.xz"
                elif download_url.endswith(".tar.gz"): pkg_format = ".tar.gz"
                elif download_url.endswith(".tar.xz"): pkg_format = ".tar.xz"
                else: pkg_format = Path(download_url).suffix
            else:
                raise UnsupportedFormatError(_("No se puede determinar el formato: el paquete no tiene 'format' ni 'download_url'."))

        if not pkg_format:
            raise UnsupportedFormatError(_("No se pudo determinar el formato del paquete desde la URL o los metadatos."))

        handler_class = self.handler_map.get(pkg_format)
        if not handler_class:
            raise UnsupportedFormatError(_("El formato de paquete '{}' no es compatible.").format(pkg_format))

        self.logger.info(_("Usando manejador: [bold yellow]{}[/bold yellow]").format(handler_class.__name__))
        return handler_class

    def _load_db(self) -> dict:
        if not self.config.BD_PAQUETES_INSTALADOS.exists(): return {}
        try:
            with open(self.config.BD_PAQUETES_INSTALADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(_("No se pudo leer la base de datos de paquetes. Creando una nueva. Error: {}").format(e))
            return {}

    def _save_db(self, db: dict):
        try:
            with open(self.config.BD_PAQUETES_INSTALADOS, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
        except IOError as e:
            raise CriticalTPTError(_("No se pudo escribir en la base de datos de paquetes: {}").format(e))

    def _verify_checksum(self, file_path: Path, expected_sha256: str):
        self.logger.info(_("Verificando suma de comprobación (checksum)..."))
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            calculated_sha256 = sha256.hexdigest()
            if calculated_sha256 == expected_sha256:
                self.logger.success(_("Suma de comprobación verificada correctamente."))
            else:
                raise VerificationError(_("¡Suma de comprobación no coincide! Esperado: {}, Calculado: {}. El archivo puede estar corrupto o manipulado.").format(expected_sha256, calculated_sha256))
        except IOError as e:
            raise VerificationError(_("No se pudo leer el archivo para verificar el checksum: {}").format(e))

    def _get_repo_urls(self) -> list[str]:
        if not self.config.ARCHIVO_REPOS.exists():
            self.logger.info(_("Archivo de repositorios no encontrado. Creando uno con los valores por defecto."))
            self.config.ARCHIVO_REPOS.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.ARCHIVO_REPOS, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.config.REPOS_POR_DEFECTO) + "\n")
            return self.config.REPOS_POR_DEFECTO
        with open(self.config.ARCHIVO_REPOS, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    def _fetch_manifest(self, repo_url: str) -> dict | None:
        manifest_url = repo_url.rstrip('/') + "/" + self.config.ARCHIVO_MANIFIESTO_REPO
        cache_path = self.config.DIR_CACHE_REPOS / hashlib.sha256(manifest_url.encode()).hexdigest()
        try:
            self.logger.debug(_("Buscando manifiesto en {}").format(manifest_url))
            response = self._session.get(manifest_url, timeout=15)
            response.raise_for_status()
            manifest_data = response.json()
            with open(cache_path, 'w', encoding='utf-8') as f: json.dump(manifest_data, f)
            return manifest_data
        except (requests.RequestException, json.JSONDecodeError) as e:
            self.logger.warning(_("No se pudo obtener el manifiesto de {}: {}").format(repo_url, e))
            if cache_path.exists():
                self.logger.info(_("Usando manifiesto cacheado para {}.").format(repo_url))
                with open(cache_path, 'r', encoding='utf-8') as f: return json.load(f)
            return None

    def _search_tpt_repos(self, term: str, results_list: list):
        self.logger.info(_("Buscando en repositorios TPT..."))
        repo_urls = self._get_repo_urls()
        for repo_url in repo_urls:
            manifest = self._fetch_manifest(repo_url)
            if not manifest or 'packages' not in manifest: continue
            for pkg_name, pkg_details in manifest['packages'].items():
                search_fields = [pkg_name, pkg_details.get('description', ''), ' '.join(pkg_details.get('keywords', []))]
                if any(term.lower() in field.lower() for field in search_fields):
                    pkg_details.update({'name': pkg_name, 'source': 'tpt', 'repository_url': repo_url, 'description': pkg_details.get('description', _('Sin descripción'))})
                    results_list.append(pkg_details)
        self.logger.info(_("Búsqueda en TPT finalizada."))

    def _search_apt(self, term: str, results_list: list):
        if not system.check_dependency("apt-cache"): return
        self.logger.info(_("Buscando en APT..."))
        try:
            result = system.execute_command(["apt-cache", "search", term], self.logger)
            for line in result.stdout.strip().split('\n'):
                if not line: continue
                parts = line.split(' - ', 1)
                results_list.append({'name': parts[0].strip(),'description': parts[1].strip() if len(parts) > 1 else _("Sin descripción"),'version': 'N/A', 'source': 'apt', 'format': 'deb'})
        except TPTError as e:
            self.logger.error(_("Fallo al buscar en APT: {}").format(e))

    def _search_flatpak(self, term: str, results_list: list):
        if not system.check_dependency("flatpak"): return
        self.logger.info(_("Buscando en Flatpak..."))
        try:
            result = system.execute_command(["flatpak", "search", term], self.logger)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split('\t')
                    results_list.append({'name': parts[2].strip(), 'description': parts[1].strip(), 'version': parts[3].strip(), 'source': 'flatpak', 'format': 'flatpak'})
        except TPTError as e:
            self.logger.error(_("Fallo al buscar en Flatpak: {}").format(e))

    def _search_snap(self, term: str, results_list: list):
        if not system.check_dependency("snap"): return
        self.logger.info(_("Buscando en Snap Store..."))
        try:
            result = system.execute_command(["snap", "find", term], self.logger)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = [p for p in line.split(' ') if p]
                    results_list.append({'name': parts[0].strip(), 'version': parts[1].strip(), 'description': ' '.join(parts[3:]).strip(), 'source': 'snap', 'format': 'snap'})
        except TPTError as e:
            self.logger.error(_("Fallo al buscar en Snap: {}").format(e))

    def search(self, term: str) -> list[dict]:
        self.logger.info(_("Iniciando búsqueda universal para '{}'...").format(term))
        results = []
        threads = []
        search_sources = [self._search_tpt_repos, self._search_apt, self._search_flatpak, self._search_snap]
        for source_func in search_sources:
            thread = threading.Thread(target=source_func, args=(term, results))
            threads.append(thread)
            thread.start()
        for thread in threads: thread.join()
        self.logger.success(_("Búsqueda universal completada. Se encontraron {} resultados en total.").format(len(results)))
        return results

    def _check_url_exists(self, url: str) -> bool:
        try:
            response = self._session.head(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _search_by_convention(self, package_name: str) -> dict | None:
        self.logger.info(_("Buscando por convención para '{}'...").format(package_name))
        fallback_extensions = [".deb", ".sh", ".py", ".AppImage", ".tar.gz", ".zip"]
        for ext in fallback_extensions:
            package_info = self._try_convention_url(package_name, ext)
            if package_info: return package_info
        return None

    def _try_convention_url(self, package_name: str, extension: str) -> dict | None:
        repos = self._get_repo_urls()
        try:
            with open(self.config.ARCHIVO_RAMA, 'r') as f: rama = f.read().strip()
        except (IOError, FileNotFoundError):
            rama = self.config.RAMA_POR_DEFECTO
        for repo_base_url_raw in repos:
            if 'github.com' in repo_base_url_raw:
                repo_path = repo_base_url_raw.split('github.com/')[-1].split('/raw/')[0].strip('/')
                repo_base_url = f"https://raw.githubusercontent.com/{repo_path}/"
            else:
                repo_base_url = repo_base_url_raw.rstrip('/') + '/'
            package_filename = f"{package_name}{extension}"
            final_url = f"{repo_base_url}{rama}/{package_filename}"
            self.logger.debug(_("Intentando URL por convención: {}").format(final_url))
            if self._check_url_exists(final_url):
                self.logger.success(_("¡URL válida encontrada por convención! {}").format(final_url))
                return {'name': package_name, 'download_url': final_url, 'format': extension, 'version': '0.0.0-conv', 'description': _('Paquete instalado por convención. Metadatos no disponibles.'), 'repository_url': repo_base_url}
        return None

    def install(self, package_name: str, source: str | None = None):
        self.logger.info(_("Resolviendo paquete para instalación: [bold magenta]{}[/bold magenta]...").format(package_name))
        search_results = self.search(package_name)
        exact_matches = [p for p in search_results if p['name'].lower() == package_name.lower()]
        if source: exact_matches = [p for p in exact_matches if p.get('source') == source]
        if not exact_matches:
            if source is None or source == 'tpt':
                self.logger.warning(_("No se encontró '{}' en manifiestos o gestores. Intentando fallback por convención...").format(package_name))
                package_info = self._search_by_convention(package_name)
                if package_info: exact_matches = [package_info]
        if not exact_matches:
            self.logger.warning(_("No se encontró '{}'. Intentando fallback por clonación de Git...").format(package_name))
            package_info = self._search_in_git_repos(package_name)
            if package_info: exact_matches = [package_info]
        if not exact_matches:
            raise PackageNotFoundError(_("Paquete '{}' no encontrado en ninguna fuente (incluyendo todos los fallbacks).").format(package_name))
        package_to_install = None
        if len(exact_matches) == 1:
            package_to_install = exact_matches[0]
        else:
            if not source:
                raise MultipleSourcesFoundError(package_name, exact_matches)
            package_to_install = exact_matches[0]
        self._perform_installation(package_to_install)

    def _perform_installation(self, package_info: dict):
        source = package_info.get("source")
        name = package_info.get("name")
        self.logger.info(_("Iniciando instalación de '{}' desde la fuente '{}'...").format(name, source))
        if source in ["apt", "flatpak", "snap"]:
            is_root = source in ["apt", "snap"]
            command = []
            if source == "apt": command = ["apt-get", "install", "-y", name]
            if source == "flatpak": command = ["flatpak", "install", "-y", name]
            if source == "snap": command = ["snap", "install", name]
            system.execute_command(command, self.logger, as_root=is_root)
            self.logger.success(_("Paquete '{}' instalado con éxito a través de {}.").format(name, source.upper()))
            return
        temp_path = None
        if "download_url" in package_info:
            download_url = package_info["download_url"]
            file_name = Path(download_url).name
            temp_path = self.config.DIR_CACHE / "downloads" / file_name
            downloader.download_file(download_url, temp_path, self.logger, progress_callback=self.progress_callback)
            if "sha256" in package_info:
                self._verify_checksum(temp_path, package_info["sha256"])
        HandlerClass = self._get_handler_class(package_info)
        handler = HandlerClass(self, package_info, self.config, self.logger, temp_path=temp_path)
        installation_details = handler.install()
        db = self._load_db()
        db[name] = {"version": package_info.get("version", "0.0.0"), "source": package_info.get("source", "tpt"), "repository_url": package_info.get("repository_url"), "installation_details": installation_details}
        self._save_db(db)
        if temp_path: temp_path.unlink(missing_ok=True)
        self.logger.success(_("¡Paquete TPT '{}' instalado con éxito!").format(name))

    def install_from_staged_file(self, package_name: str, staged_filename: str | None):
        self.logger.info(_("Instalando paquete preparado [bold magenta]{}[/bold magenta] desde AADPO...").format(package_name))
        search_results = self.search(package_name)
        if not search_results:
            raise PackageNotFoundError(_("No se encontró información del paquete '{}' en los repositorios para la instalación preparada.").format(package_name))
        package_info = search_results[0]
        staged_file_path = None
        if staged_filename:
            staged_file_path = self.config.DIR_STAGING / "files" / staged_filename
            if not staged_file_path.exists():
                raise TPTError(_("El archivo preparado '{}' no se encuentra en la zona de espera.").format(staged_filename))
        self._perform_installation(package_info)

    def uninstall(self, package_name: str):
        self.logger.info(_("Iniciando desinstalación de [bold magenta]{}[/bold magenta]...").format(package_name))
        db = self._load_db()
        if package_name in db:
            package_data = db[package_name]
            source = package_data.get("source", "tpt")
            self.logger.info(_("El paquete fue instalado por TPT (fuente: {}). Usando manejador de TPT.").format(source))
            installation_details = package_data.get("installation_details", {})
            handler_name = installation_details.get("handler")
            if not handler_name:
                raise TPTError(_("No se puede desinstalar: no se encontró el nombre del manejador en la base de datos de TPT."))
            HandlerClass = next((cls for cls in self.handler_map.values() if cls.__name__ == handler_name), None)
            if not HandlerClass:
                raise UnsupportedFormatError(_("El manejador '{}' necesario para la desinstalación no se encuentra.").format(handler_name))
            handler = HandlerClass(self, {"name": package_name}, self.config, self.logger)
            handler.uninstall(installation_details)
            del db[package_name]
            self._save_db(db)
            self.logger.success(_("¡Paquete '{}' desinstalado con éxito de TPT!").format(package_name))
        else:
            self.logger.info(_("El paquete no está en la base de datos de TPT. Intentando desinstalación con gestores del sistema..."))
            uninstalled = False
            if system.check_dependency("apt-get"):
                try:
                    check_cmd = ["dpkg", "-l", package_name]
                    result = system.execute_command(check_cmd, self.logger)
                    if result.returncode == 0 and "ii" in result.stdout.split('\n')[5]:
                        system.execute_command(["apt-get", "remove", "-y", package_name], self.logger, as_root=True)
                        self.logger.success(_("Paquete '{}' desinstalado con éxito a través de APT.").format(package_name))
                        uninstalled = True
                except TPTError: pass
            if not uninstalled and system.check_dependency("flatpak"):
                try:
                    check_cmd = ["flatpak", "list", "--columns=application"]
                    result = system.execute_command(check_cmd, self.logger)
                    if package_name in result.stdout:
                        system.execute_command(["flatpak", "uninstall", "-y", package_name], self.logger)
                        self.logger.success(_("Paquete '{}' desinstalado con éxito a través de Flatpak.").format(package_name))
                        uninstalled = True
                except TPTError: pass
            if not uninstalled and system.check_dependency("snap"):
                try:
                    check_cmd = ["snap", "list"]
                    result = system.execute_command(check_cmd, self.logger)
                    if package_name in result.stdout:
                        system.execute_command(["snap", "remove", package_name], self.logger, as_root=True)
                        self.logger.success(_("Paquete '{}' desinstalado con éxito a través de Snap.").format(package_name))
                        uninstalled = True
                except TPTError: pass
            if not uninstalled:
                raise PackageNotFoundError(_("El paquete '{}' no se encontró ni en TPT ni en los gestores de paquetes del sistema compatibles.").format(package_name))

    def list_installed(self) -> dict:
        return self._load_db()

    def upgrade(self, no_apply: bool = False):
        self.logger.info(_("[bold blue]Iniciando proceso de actualización de TPT...[/bold blue]"))
        self.logger.info(_("\n[bold]Paso 1: Buscando actualizaciones disponibles[/bold]"))
        tpt_updates = self._find_tpt_updates()
        system_updates = self._find_system_updates()
        if not tpt_updates and not any(system_updates.values()):
            self.logger.success(_("\n¡Todo está ya actualizado!"))
            return
        if no_apply:
            self.logger.info(_("\n[bold]Paso 2: Preparando actualizaciones para AADPO (sin aplicar)[/bold]"))
            self._stage_updates(tpt_updates, system_updates)
        else:
            self.logger.info(_("\n[bold]Paso 2: Aplicando actualizaciones directamente[/bold]"))
            self._apply_system_updates_sources()
            self._apply_tpt_updates(tpt_updates)
            self._apply_system_package_updates(system_updates)
        self.logger.success(_("\n[bold green]¡Proceso de actualización de TPT completado![/bold green]"))

    def _find_tpt_updates(self) -> list[dict]:
        self.logger.info(_("Buscando actualizaciones para paquetes de TPT..."))
        installed_packages = self._load_db()
        packages_to_upgrade = []
        if not installed_packages: return []
        self._update_git_repos_and_check_for_updates(installed_packages, packages_to_upgrade)
        for name, details in installed_packages.items():
            if details.get("source") == "tpt-git": continue
            installed_version_str = details.get("version", "0.0.0")
            try:
                search_results = self.search(name)
                tpt_results = [r for r in search_results if r.get("source") == "tpt"]
                if not tpt_results: continue
                latest_info = tpt_results[0]
                latest_version_str = latest_info.get("version", "0.0.0")
                if parse_version(latest_version_str) > parse_version(installed_version_str):
                    if not any(p['name'] == name for p in packages_to_upgrade):
                        self.logger.info(_("[green]  - Actualización para [magenta]{}[/magenta]: v{} -> v{}[/green]").format(name, installed_version_str, latest_version_str))
                        packages_to_upgrade.append(latest_info)
            except Exception as e:
                self.logger.error(_("No se pudo comprobar la actualización para '{}': {}").format(name, e))
        return packages_to_upgrade

    def _update_git_repos_and_check_for_updates(self, installed_packages: dict, packages_to_upgrade: list):
        if not self.config.DIR_GIT_CLONES.exists(): return
        self.logger.info(_("Actualizando repositorios Git clonados..."))
        for repo_path in self.config.DIR_GIT_CLONES.iterdir():
            if repo_path.is_dir() and (repo_path / ".git").exists():
                self.logger.info(_("Haciendo 'git pull' en [cyan]{}[/cyan]...").format(repo_path.name))
                try:
                    original_cwd = Path.cwd()
                    os.chdir(repo_path)
                    system.execute_command(["git", "pull"], self.logger)
                    os.chdir(original_cwd)
                    manifest_path = repo_path / self.config.ARCHIVO_MANIFIESTO_REPO
                    if not manifest_path.exists(): continue
                    with open(manifest_path, "r", encoding="utf-8") as f: manifest = json.load(f)
                    for name, details in installed_packages.items():
                        if details.get("installation_details", {}).get("clone_path") == str(repo_path):
                            installed_version_str = details.get("version", "0.0.0")
                            latest_pkg_details = manifest.get("packages", {}).get(name)
                            if latest_pkg_details:
                                latest_version_str = latest_pkg_details.get("version", "0.0.0")
                                if parse_version(latest_version_str) > parse_version(installed_version_str):
                                    self.logger.info(_("[green]  - Actualización para [magenta]{}[/magenta] (Git): v{} -> v{}[/green]").format(name, installed_version_str, latest_version_str))
                                    latest_pkg_details.update({'name': name, 'source': 'tpt-git', 'clone_path': str(repo_path)})
                                    packages_to_upgrade.append(latest_pkg_details)
                except (TPTError, json.JSONDecodeError, Exception) as e:
                    self.logger.error(_("No se pudo actualizar o comprobar el repositorio '{}': {}").format(repo_path.name, e))
                finally:
                    if 'original_cwd' in locals() and Path.cwd() != original_cwd:
                        os.chdir(original_cwd)

    def _find_system_updates(self) -> dict:
        self.logger.info(_("Detectando gestores de paquetes del sistema..."))
        updates = {"apt": system.check_dependency("apt"), "flatpak": system.check_dependency("flatpak"), "snap": system.check_dependency("snap")}
        self.logger.info(_("Gestores detectados: {}").format([k for k, v in updates.items() if v]))
        return updates

    def _stage_updates(self, tpt_updates: list[dict], system_updates: dict):
        staging_dir = self.config.DIR_STAGING
        staging_files_dir = staging_dir / "files"
        staging_files_dir.mkdir(exist_ok=True, parents=True)
        actions = []
        for pkg_info in tpt_updates:
            action = {"action": "install_tpt", "name": pkg_info["name"]}
            if "download_url" in pkg_info:
                url = pkg_info["download_url"]
                filename = Path(url).name
                dest_path = staging_files_dir / filename
                self.logger.info(_("Descargando {} para preparación...").format(filename))
                downloader.download_file(url, dest_path, self.logger)
                action["file"] = str(filename)
            actions.append(action)
        for manager, available in system_updates.items():
            if available: actions.append({"action": "sys_update", "manager": manager})
        manifest_path = staging_dir / "aadpo_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f: json.dump({"actions": actions}, f, indent=4)
        self.logger.success(_("Actualizaciones preparadas en {}. Se aplicarán en el próximo reinicio/apagado si AADPO está integrado.").format(staging_dir))

    def _apply_tpt_updates(self, tpt_updates: list[dict]):
        if not tpt_updates:
            self.logger.info(_("No hay paquetes de TPT para actualizar."))
            return
        self.logger.info(_("Se actualizarán los siguientes paquetes de TPT: {}").format([p['name'] for p in tpt_updates]))
        for pkg_info in tpt_updates:
            try:
                self.install(pkg_info['name'])
            except Exception as e:
                self.logger.error(_("Falló la actualización de '{}': {}").format(pkg_info['name'], e))

    def _apply_system_updates_sources(self):
        if system.check_dependency("apt"):
            try:
                self.logger.info(_("Ejecutando 'apt update'..."))
                system.execute_command(["apt", "update"], self.logger, as_root=True)
            except TPTError as e:
                self.logger.error(_("Falló 'apt update': {}").format(e))

    def _apply_system_package_updates(self, system_updates: dict):
        self.logger.info(_("Actualizando paquetes del sistema..."))
        if system_updates.get("apt"):
            try:
                self.logger.info(_("--- Salida de APT Upgrade ---"))
                system.execute_command(["apt-get", "upgrade", "-y"], self.logger, as_root=True, stream_output=True)
                system.execute_command(["apt-get", "autoclean", "-y"], self.logger, as_root=True)
                self.logger.info(_("--- Fin de la Salida de APT ---"))
            except TPTError as e: self.logger.error(_("Falló la actualización de APT: {}").format(e))
        if system_updates.get("flatpak"):
            try:
                self.logger.info(_("--- Salida de Flatpak Update ---"))
                system.execute_command(["flatpak", "update", "-y"], self.logger, stream_output=True)
                self.logger.info(_("--- Fin de la Salida de Flatpak ---"))
            except TPTError as e: self.logger.error(_("Falló la actualización de Flatpak: {}").format(e))
        if system_updates.get("snap"):
            try:
                self.logger.info(_("--- Salida de Snap Refresh ---"))
                system.execute_command(["snap", "refresh"], self.logger, as_root=True, stream_output=True)
                self.logger.info(_("--- Fin de la Salida de Snap ---"))
            except TPTError as e: self.logger.error(_("Falló la actualización de Snap: {}").format(e))

    def system_integrate_install(self):
        self.logger.info(_("Integrando AADPO con systemd..."))
        if not system.check_dependency("systemctl"):
            raise CriticalTPTError(_("No se encontró 'systemctl'. No se puede integrar con el sistema."))
        tpt_script_path = Path(sys.argv[0]).resolve()
        apply_script_path = tpt_script_path.parent / "tpt-apply-updates"
        if not apply_script_path.exists():
            raise CriticalTPTError(_("No se encuentra el script '{}'. No se puede crear el servicio.").format(apply_script_path))
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
        self.logger.info(_("Creando fichero de servicio en {}").format(service_path))
        try:
            command = ["tee", str(service_path)]
            system.execute_command(command, self.logger, as_root=True, input=service_content)
            self.logger.info(_("Recargando demonio de systemd..."))
            system.execute_command(["systemctl", "daemon-reload"], self.logger, as_root=True)
            self.logger.info(_("Activando servicio '{}'...").format(service_name))
            system.execute_command(["systemctl", "enable", service_name], self.logger, as_root=True)
            self.logger.success(_("¡Servicio AADPO instalado y activado con éxito!"))
            self.logger.info(_("Las actualizaciones preparadas con 'tpt upgrade --no-apply' se instalarán al apagar o reiniciar."))
        except TPTError as e:
            raise TPTError(_("Falló la instalación del servicio de systemd: {}").format(e))

    def system_integrate_uninstall(self):
        self.logger.info(_("Desinstalando el servicio AADPO de systemd..."))
        if not system.check_dependency("systemctl"):
            raise CriticalTPTError(_("No se encontró 'systemctl'. No se puede desinstalar el servicio."))
        service_name = "tpt-aadpo.service"
        service_path = Path(f"/etc/systemd/system/{service_name}")
        try:
            if service_path.exists():
                self.logger.info(_("Desactivando servicio '{}'...").format(service_name))
                system.execute_command(["systemctl", "disable", service_name], self.logger, as_root=True)
                self.logger.info(_("Eliminando fichero de servicio {}...").format(service_path))
                system.execute_command(["rm", "-f", str(service_path)], self.logger, as_root=True)
                self.logger.info(_("Recargando demonio de systemd..."))
                system.execute_command(["systemctl", "daemon-reload"], self.logger, as_root=True)
                self.logger.success(_("¡Servicio AADPO desinstalado con éxito!"))
            else:
                self.logger.warning(_("El servicio AADPO no parece estar instalado."))
        except TPTError as e:
            raise TPTError(_("Falló la desinstalación del servicio de systemd: {}").format(e))

    def _search_in_git_repos(self, package_name: str) -> dict | None:
        if not system.check_dependency("git"):
            self.logger.warning(_("Comando 'git' no encontrado. Saltando búsqueda en repositorios Git."))
            return None
        repo_urls = self._get_repo_urls()
        for repo_url_raw in repo_urls:
            clone_url, repo_name = None, None
            if "raw.githubusercontent.com" in repo_url_raw:
                parts = repo_url_raw.split('/')
                if len(parts) >= 5:
                    user, repo = parts[3], parts[4]
                    clone_url, repo_name = f"https://github.com/{user}/{repo}.git", repo
            elif repo_url_raw.endswith(".git"):
                clone_url, repo_name = repo_url_raw, Path(repo_url_raw).stem
            if not clone_url: continue
            try:
                clone_path = self.config.DIR_GIT_CLONES / repo_name
                if not clone_path.exists():
                    self.logger.info(_("Clonando rama 'regular' de '{}' en '{}'...").format(clone_url, clone_path))
                    clone_cmd = ["git", "clone", "--branch", "regular", "--single-branch", clone_url, str(clone_path)]
                    system.execute_command(clone_cmd, self.logger)
                manifest_path = clone_path / self.config.ARCHIVO_MANIFIESTO_REPO
                if manifest_path.exists():
                    self.logger.info(_("Buscando '{}' en el manifiesto local de '{}'...").format(package_name, repo_name))
                    with open(manifest_path, "r", encoding="utf-8") as f: manifest = json.load(f)
                    pkg_details = manifest.get("packages", {}).get(package_name)
                    if pkg_details:
                        self.logger.success(_("¡Paquete '{}' encontrado en el repositorio Git clonado '{}'!").format(package_name, repo_name))
                        pkg_details.update({'name': package_name, 'source': 'tpt-git', 'repository_url': clone_url, 'clone_path': str(clone_path)})
                        return pkg_details
            except (TPTError, json.JSONDecodeError, Exception) as e:
                self.logger.error(_("No se pudo procesar el repositorio Git '{}': {}").format(clone_url, e))
                continue
        return None

    def get_aadpo_status(self) -> list[dict] | None:
        manifest_path = self.config.DIR_STAGING / "aadpo_manifest.json"
        if not manifest_path.exists(): return None
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            return manifest.get("actions", [])
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(_("No se pudo leer el manifiesto de AADPO: {}").format(e))
            return []
