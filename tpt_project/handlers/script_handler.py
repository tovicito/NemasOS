from pathlib import Path
from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command
from ..utils.exceptions import TPTError

class ScriptHandler(BaseHandler):
    """Manejador para instalar y desinstalar paquetes basados en scripts."""

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger, **kwargs)
        self.temp_path = temp_path

    def install(self) -> dict:
        """
        Mueve el script a un directorio de ejecutables, le da permisos y crea un .desktop.
        """
        install_path = self.config.DIR_EJECUTABLES_ROOT / self.app_name
        self.logger.info(f"Instalando script en {install_path}...")

        try:
            # Mover el archivo a su destino final
            execute_command(["mv", str(self.temp_path), str(install_path)], self.logger, as_root=True)
            # Darle permisos de ejecución
            execute_command(["chmod", "+x", str(install_path)], self.logger, as_root=True)
        except TPTError as e:
            raise TPTError(f"No se pudo instalar el script en {install_path}: {e}")

        # Crear archivo .desktop si hay metadatos
        desktop_file_path = self._create_desktop_file(install_path)

        self.logger.success(f"Script '{self.app_name}' instalado correctamente en {install_path}.")

        details = super().install()
        details.update({
            "install_path": str(install_path),
            "desktop_file": desktop_file_path
        })
        return details

    def uninstall(self, installation_details: dict):
        """
        Elimina el script y su archivo .desktop asociado.
        """
        install_path = installation_details.get("install_path")
        if not install_path:
            raise TPTError("No se puede desinstalar: falta 'install_path' en los detalles de instalación.")

        path_to_remove = Path(install_path)
        if path_to_remove.exists():
            self.logger.info(f"Eliminando script desde {path_to_remove}...")
            try:
                execute_command(["rm", "-f", str(path_to_remove)], self.logger, as_root=True)
                self.logger.success(f"Script '{self.app_name}' eliminado.")
            except TPTError as e:
                self.logger.warning(f"No se pudo eliminar el script {path_to_remove}: {e}")
        else:
            self.logger.warning(f"El script a desinstalar no se encontró en {path_to_remove}. Omitiendo.")

        # Limpiar el archivo .desktop
        self._cleanup_desktop_file(installation_details)
