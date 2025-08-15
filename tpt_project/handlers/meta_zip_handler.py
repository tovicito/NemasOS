import json
import tempfile
from pathlib import Path
from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError, VerificationError

class MetaZipHandler(BaseHandler):
    """
    Manejador para meta-paquetes .zip. Descomprime y luego instala cada
    sub-paquete listado en un manifiesto interno.
    """

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger, **kwargs)
        self.temp_path = temp_path
        if not check_dependency("unzip"):
            raise CriticalTPTError("El comando 'unzip' no se encuentra. TPT no puede gestionar meta-paquetes .zip.")

    def install(self) -> dict:
        """Descomprime el meta-paquete e instala cada sub-paquete."""

        with tempfile.TemporaryDirectory(prefix="tpt_meta_") as extract_dir_str:
            extract_dir = Path(extract_dir_str)
            self.logger.info(f"Extrayendo meta-paquete en: {extract_dir}")

            try:
                execute_command(["unzip", str(self.temp_path), "-d", str(extract_dir)], self.logger)
            except TPTError as e:
                raise TPTError(f"No se pudo descomprimir el meta-paquete .zip: {e}")

            manifest_path = extract_dir / "manifest.json"
            if not manifest_path.exists():
                raise VerificationError("El meta-paquete .zip es inválido: no se encontró 'manifest.json' en su interior.")

            with open(manifest_path, "r", encoding="utf-8") as f:
                sub_manifest = json.load(f)

            installed_sub_packages = []
            sub_packages = sub_manifest.get("packages", [])
            self.logger.info(f"Se encontraron {len(sub_packages)} sub-paquetes en el manifiesto interno.")

            for sub_pkg_info in sub_packages:
                sub_pkg_name = sub_pkg_info.get("name")
                sub_pkg_file = sub_pkg_info.get("file")

                if not all([sub_pkg_name, sub_pkg_file]):
                    self.logger.warning(f"Entrada de sub-paquete inválida en manifest.json: {sub_pkg_info}. Omitiendo.")
                    continue

                sub_pkg_path = extract_dir / sub_pkg_file
                if not sub_pkg_path.exists():
                    self.logger.error(f"El archivo del sub-paquete '{sub_pkg_file}' no se encontró dentro del .zip. Omitiendo.")
                    continue

                try:
                    self.logger.info(f"--- Iniciando instalación del sub-paquete: [bold cyan]{sub_pkg_name}[/bold cyan] ---")
                    # Usamos el método interno para instalar desde un fichero local
                    self.pm._perform_installation(sub_pkg_info, sub_pkg_path)
                    installed_sub_packages.append(sub_pkg_name)
                    self.logger.info(f"--- Sub-paquete '{sub_pkg_name}' instalado. ---")
                except Exception as e:
                    self.logger.error(f"Falló la instalación del sub-paquete '{sub_pkg_name}': {e}")

            if not installed_sub_packages:
                raise TPTError("No se pudo instalar ninguno de los sub-paquetes del meta-paquete.")

        return {
            "handler": "MetaZipHandler",
            "installed_sub_packages": installed_sub_packages
        }

    def uninstall(self, installation_details: dict):
        """Desinstala todos los sub-paquetes que fueron instalados por este meta-paquete."""
        sub_packages = installation_details.get("installed_sub_packages", [])
        if not sub_packages:
            self.logger.warning(f"No se encontraron sub-paquetes para desinstalar para '{self.app_name}'.")
            return

        self.logger.info(f"Desinstalando {len(sub_packages)} sub-paquetes de '{self.app_name}'...")
        for sub_pkg_name in sub_packages:
            try:
                self.pm.uninstall(sub_pkg_name)
            except Exception as e:
                self.logger.error(f"Falló la desinstalación del sub-paquete '{sub_pkg_name}': {e}")

        self.logger.success(f"Meta-paquete '{self.app_name}' desinstalado.")
