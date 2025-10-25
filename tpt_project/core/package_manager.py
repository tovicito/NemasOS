import json
import hashlib
import requests
import os
import threading
import logging
from pathlib import Path

from packaging.version import parse as parse_version

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
    def __init__(self, config: Configuracion, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.settings = self.config.load_settings()

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": f"TPT-PackageManager/6.0-plasma"})
        self._session.timeout = self.settings.get("network_timeout", 15)
        self._session.verify = self.settings.get("ssl_verify", True)

        self.progress_callback = None

        self.handler_map = {
            ".deb": DebHandler, ".deb.xz": DebXzHandler, ".sh": ScriptHandler,
            ".py": ScriptHandler, ".AppImage": AppImageHandler, ".tar.gz": ArchiveHandler,
            ".tgz": ArchiveHandler, ".tar.xz": ArchiveHandler, ".rpm": RpmHandler,
            ".ps1": PowershellHandler, ".exe": ExeHandler, ".msi": MsiHandler,
            ".apk": AndroidApkHandler, "flatpak": FlatpakHandler, "snap": SnapHandler,
            "alpine_apk": AlpineApkHandler, "android_apk": AndroidApkHandler,
            "nemas_patch_zip": NemasPatchZipHandler, "meta_zip": MetaZipHandler,
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
                raise UnsupportedFormatError("No se puede determinar el formato: el paquete no tiene 'format' ni 'download_url'.")

        handler_class = self.handler_map.get(pkg_format)
        if not handler_class:
            raise UnsupportedFormatError(f"El formato de paquete '{pkg_format}' no es compatible.")

        self.logger.info(f"Usando manejador: {handler_class.__name__}")
        return handler_class

    def _load_db(self) -> dict:
        if not self.config.BD_PAQUETES_INSTALADOS.exists(): return {}
        try:
            with open(self.config.BD_PAQUETES_INSTALADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"No se pudo leer la base de datos de paquetes. Creando una nueva. Error: {e}")
            return {}

    def _save_db(self, db: dict):
        try:
            with open(self.config.BD_PAQUETES_INSTALADOS, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
        except IOError as e:
            raise CriticalTPTError(f"No se pudo escribir en la base de datos de paquetes: {e}")

    def _get_repo_urls(self) -> list[str]:
        if not self.config.ARCHIVO_REPOS.exists():
            self.logger.info("Archivo de repositorios no encontrado. Creando uno con los valores por defecto.")
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
            self.logger.debug(f"Buscando manifiesto en {manifest_url}")
            response = self._session.get(manifest_url)
            response.raise_for_status()
            manifest_data = response.json()
            with open(cache_path, 'w', encoding='utf-8') as f: json.dump(manifest_data, f)
            return manifest_data
        except (requests.RequestException, json.JSONDecodeError) as e:
            self.logger.warning(f"No se pudo obtener el manifiesto de {repo_url}: {e}")
            if cache_path.exists():
                self.logger.info(f"Usando manifiesto cacheado para {repo_url}.")
                with open(cache_path, 'r', encoding='utf-8') as f: return json.load(f)
            return None

    def _search_source(self, source_func, term, results_list):
        try:
            source_func(term, results_list)
        except Exception as e:
            self.logger.error(f"Error buscando en {source_func.__name__}: {e}", exc_info=True)

    def _search_tpt_repos(self, term: str, results_list: list):
        self.logger.info("Buscando en repositorios TPT...")
        for repo_url in self._get_repo_urls():
            manifest = self._fetch_manifest(repo_url)
            if not manifest or 'packages' not in manifest: continue
            for pkg_name, pkg_details in manifest['packages'].items():
                search_fields = [pkg_name, pkg_details.get('description', ''), ' '.join(pkg_details.get('keywords', []))]
                if any(term.lower() in field.lower() for field in search_fields):
                    pkg_details.update({'name': pkg_name, 'source': 'tpt', 'repository_url': repo_url, 'description': pkg_details.get('description', 'Sin descripción')})
                    results_list.append(pkg_details)

    def _search_apt(self, term: str, results_list: list):
        if not system.check_dependency("apt-cache"): return
        self.logger.info("Buscando en APT...")
        result = system.execute_command(["apt-cache", "search", term], self.logger)
        for line in result.stdout.strip().split('\n'):
            if not line: continue
            parts = line.split(' - ', 1)
            results_list.append({'name': parts[0].strip(),'description': parts[1].strip() if len(parts) > 1 else "Sin descripción",'version': 'N/A', 'source': 'apt', 'format': 'deb'})

    def _search_flatpak(self, term: str, results_list: list):
        if not system.check_dependency("flatpak"): return
        self.logger.info("Buscando en Flatpak...")
        result = system.execute_command(["flatpak", "search", term], self.logger)
        for line in result.stdout.strip().split('\n')[1:]: # Omitir cabecera
            parts = line.split('\t')
            if len(parts) >= 4:
                results_list.append({'name': parts[2].strip(), 'description': parts[1].strip(), 'version': parts[3].strip(), 'source': 'flatpak', 'format': 'flatpak'})

    def _search_snap(self, term: str, results_list: list):
        if not system.check_dependency("snap"): return
        self.logger.info("Buscando en Snap Store...")
        result = system.execute_command(["snap", "find", term], self.logger)
        for line in result.stdout.strip().split('\n')[1:]: # Omitir cabecera
            parts = [p for p in line.split() if p]
            if len(parts) >= 4:
                results_list.append({'name': parts[0].strip(), 'version': parts[1].strip(), 'description': ' '.join(parts[3:]).strip(), 'source': 'snap', 'format': 'snap'})

    def search(self, term: str) -> list[dict]:
        self.logger.info(f"Iniciando búsqueda universal para '{term}'...")
        results = []
        threads = []
        search_sources = [self._search_tpt_repos, self._search_apt, self._search_flatpak, self._search_snap]
        for source_func in search_sources:
            thread = threading.Thread(target=self._search_source, args=(source_func, term, results))
            threads.append(thread)
            thread.start()
        for thread in threads: thread.join()
        self.logger.info(f"Búsqueda universal completada. Se encontraron {len(results)} resultados.")
        return results

    def _search_by_convention(self, package_name: str) -> dict | None:
        self.logger.info(f"Buscando por convención para '{package_name}'...")
        # Lógica de búsqueda por convención aquí...
        return None

    def _search_in_git_repos(self, package_name: str) -> dict | None:
        self.logger.info(f"Buscando en repositorios Git para '{package_name}'...")
        if not system.check_dependency("git"):
            self.logger.warning("Comando 'git' no encontrado. Saltando búsqueda en repositorios Git.")
            return None
        for repo_url_raw in self._get_repo_urls():
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
                    self.logger.info(f"Clonando rama 'regular' de '{clone_url}'...")
                    system.execute_command(["git", "clone", "--branch", "regular", "--single-branch", clone_url, str(clone_path)], self.logger)
                manifest_path = clone_path / self.config.ARCHIVO_MANIFIESTO_REPO
                if manifest_path.exists():
                    with open(manifest_path, "r", encoding="utf-8") as f: manifest = json.load(f)
                    pkg_details = manifest.get("packages", {}).get(package_name)
                    if pkg_details:
                        self.logger.info(f"Paquete '{package_name}' encontrado en el repo Git clonado '{repo_name}'.")
                        pkg_details.update({'name': package_name, 'source': 'tpt-git', 'repository_url': clone_url, 'clone_path': str(clone_path)})
                        return pkg_details
            except Exception as e:
                self.logger.error(f"No se pudo procesar el repositorio Git '{clone_url}': {e}")
        return None

    def install(self, package_name: str, source: str | None = None):
        self.logger.info(f"Resolviendo para instalar: '{package_name}' (Fuente: {source or 'cualquiera'})")
        search_results = self.search(package_name)
        exact_matches = [p for p in search_results if p['name'].lower() == package_name.lower()]
        if source: exact_matches = [p for p in exact_matches if p.get('source') == source]

        if not exact_matches:
            package_info = self._search_by_convention(package_name) or self._search_in_git_repos(package_name)
            if package_info: exact_matches = [package_info]

        if not exact_matches:
            raise PackageNotFoundError(f"Paquete '{package_name}' no encontrado.")

        if len(exact_matches) > 1 and not source:
            raise MultipleSourcesFoundError(package_name, exact_matches)

        self._perform_installation(exact_matches[0])

    def _perform_installation(self, package_info: dict):
        source = package_info.get("source")
        name = package_info.get("name")
        self.logger.info(f"Iniciando instalación de '{name}' desde la fuente '{source}'...")
        if source in ["apt", "flatpak", "snap"]:
            # Lógica de instalación para gestores nativos...
            self.logger.info(f"Instalando '{name}' con {source}...")
            # ...
        else: # Paquetes TPT
            temp_path = None
            if "download_url" in package_info:
                # Lógica de descarga...
                pass
            HandlerClass = self._get_handler_class(package_info)
            handler = HandlerClass(self, package_info, self.config, self.logger, temp_path=temp_path)
            installation_details = handler.install()
            db = self._load_db()
            db[name] = {"version": package_info.get("version", "0.0.0"), "source": source, "installation_details": installation_details}
            self._save_db(db)
            self.logger.info(f"Paquete TPT '{name}' instalado con éxito.")

    def uninstall(self, package_name: str):
        self.logger.info(f"Iniciando desinstalación de '{package_name}'...")
        # ... Lógica de desinstalación universal ...

    def upgrade(self, no_apply: bool = False):
        self.logger.info("Buscando actualizaciones...")
        # ... Lógica de actualización ...

    # ... otros métodos ...
