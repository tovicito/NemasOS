import os
import logging
from pathlib import Path
from .base_handler import BaseHandler
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError
import tempfile
import datetime

class NemasPatchZipHandler(BaseHandler):
    """Manejador para aplicar parches 'Nemas' distribuidos como un .zip con un script."""

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: logging.Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger)
        self.temp_path = temp_path
        if not check_dependency("unzip"):
            raise CriticalTPTError("El comando 'unzip' no se encuentra. TPT no puede gestionar parches .zip.")

    def _find_executable(self, extract_dir: Path) -> Path | None:
        """Intenta encontrar un script ejecutable en el directorio extraído."""
        self.logger.info(f"Buscando script de parche en {extract_dir}...")
        for item in extract_dir.rglob('*'):
            # Buscar cualquier script ejecutable, no solo con nombre específico
            if item.is_file() and os.access(item, os.X_OK):
                self.logger.info(f"Encontrado script de parche ejecutable: {item}")
                return item
        return None

    def install(self) -> dict:
        """Descomprime el parche y ejecuta el script que contiene."""

        with tempfile.TemporaryDirectory(prefix="tpt_patch_") as extract_dir_str:
            extract_dir = Path(extract_dir_str)
            self.logger.info(f"Extrayendo parche en el directorio temporal: {extract_dir}")

            try:
                execute_command(["unzip", str(self.temp_path), "-d", str(extract_dir)], self.logger)
            except TPTError as e:
                raise TPTError(f"No se pudo descomprimir el archivo del parche: {e}")

            patch_script = self._find_executable(extract_dir)

            if not patch_script:
                raise TPTError("No se encontró ningún script ejecutable dentro del archivo del parche .zip.")

            self.logger.info(f"Ejecutando script de parche: {patch_script}")
            try:
                # Los scripts de parche a menudo necesitan root
                execute_command([str(patch_script)], self.logger, as_root=True, cwd=extract_dir)
                self.logger.success(f"Parche '{self.app_name}' aplicado con éxito.")
            except TPTError as e:
                raise TPTError(f"El script de parche falló: {e}")

        return {
            "handler": "NemasPatchZipHandler",
            "applied_on": datetime.datetime.utcnow().isoformat()
        }

    def uninstall(self, installation_details: dict):
        """Los parches no se pueden desinstalar de forma segura."""
        self.logger.warning(f"El paquete '{self.app_name}' es un parche y no se puede desinstalar automáticamente.")
        self.logger.warning("Si es necesario, deberás revertir los cambios manualmente.")
