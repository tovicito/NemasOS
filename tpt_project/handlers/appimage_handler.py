from pathlib import Path
from .base_handler import BaseHandler
from ..core.config import Configuracion
from ..utils.system import execute_command
from ..utils.exceptions import TPTError
import logging

class AppImageHandler(BaseHandler):
    """Manejador para instalar y desinstalar paquetes .AppImage."""

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: logging.Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger, **kwargs)
        self.temp_path = temp_path

    def install(self) -> dict:
        """
        Mueve la AppImage a /opt, la hace ejecutable y crea un enlace simbólico y un .desktop.
        """
        # Directorio de destino para todas las AppImages
        install_dir = self.config.DIR_OPT_ROOT / "AppImages"
        install_path = install_dir / f"{self.app_name}.AppImage"

        # Enlace simbólico para que esté disponible en el PATH
        symlink_path = self.config.DIR_EJECUTABLES_ROOT / self.app_name

        self.logger.info(f"Instalando AppImage en {install_path}...")

        try:
            # 1. Crear el directorio de instalación
            execute_command(["mkdir", "-p", str(install_dir)], self.logger, as_root=True)
            # 2. Mover la AppImage descargada
            execute_command(["mv", str(self.temp_path), str(install_path)], self.logger, as_root=True)
            # 3. Darle permisos de ejecución
            execute_command(["chmod", "+x", str(install_path)], self.logger, as_root=True)
            # 4. Crear el enlace simbólico (eliminando si ya existe)
            if symlink_path.exists() or symlink_path.is_symlink():
                execute_command(["rm", "-f", str(symlink_path)], self.logger, as_root=True)
            execute_command(["ln", "-s", str(install_path), str(symlink_path)], self.logger, as_root=True)

        except TPTError as e:
            raise TPTError(f"No se pudo instalar la AppImage en {install_path}: {e}")

        # 5. Crear archivo .desktop
        desktop_file_path = self._create_desktop_file(symlink_path)

        self.logger.info(f"AppImage '{self.app_name}' instalada correctamente.")

        details = super().install()
        details.update({
            "install_path": str(install_path),
            "symlink_path": str(symlink_path),
            "desktop_file": desktop_file_path
        })
        return details

    def uninstall(self, installation_details: dict):
        """
        Elimina la AppImage, su enlace simbólico y su archivo .desktop.
        """
        paths_to_remove = [
            installation_details.get("install_path"),
            installation_details.get("symlink_path")
        ]

        for path_str in paths_to_remove:
            if not path_str: continue

            path_to_remove = Path(path_str)
            if path_to_remove.exists() or path_to_remove.is_symlink():
                self.logger.info(f"Eliminando {path_to_remove}...")
                try:
                    execute_command(["rm", "-f", str(path_to_remove)], self.logger, as_root=True)
                except TPTError as e:
                    self.logger.warning(f"No se pudo eliminar {path_to_remove}: {e}")
            else:
                self.logger.warning(f"El archivo a desinstalar no se encontró en {path_to_remove}. Omitiendo.")

        # Limpiar el archivo .desktop
        self._cleanup_desktop_file(installation_details)
        self.logger.info(f"AppImage '{self.app_name}' desinstalada.")
