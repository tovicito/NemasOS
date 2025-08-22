from pathlib import Path
from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError

class DebHandler(BaseHandler):
    """Manejador para instalar y desinstalar paquetes .deb."""

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger, **kwargs)
        self.temp_path = temp_path
        if not check_dependency("dpkg"):
            raise CriticalTPTError("El comando 'dpkg' no se encuentra. Este manejador no puede funcionar sin él.")

    def install(self) -> dict:
        """Instala un paquete .deb usando dpkg."""
        self.logger.info(f"Usando 'dpkg' para instalar {self.temp_path}...")

        try:
            execute_command(["dpkg", "-i", str(self.temp_path)], self.logger, as_root=True)
            self.logger.success(f"El paquete '{self.app_name}' fue instalado por dpkg.")
            self.logger.info("Ejecutando 'apt-get install -f' para reparar posibles dependencias rotas...")
            self.repair()
        except TPTError as e:
            self.logger.error(f"Falló la instalación con dpkg. Intentando reparar dependencias...")
            self.repair()
            # Re-lanzamos el error si la reparación no soluciona el problema subyacente de dpkg
            raise TPTError(f"La instalación de '{self.app_name}' falló: {e}")

        details = super().install()
        details.update({
            "package_name": self.app_name
        })
        return details

    def uninstall(self, installation_details: dict):
        """Desinstala un paquete .deb usando dpkg."""
        package_name = installation_details.get("package_name")
        if not package_name:
            raise TPTError("No se puede desinstalar: falta 'package_name' en los detalles de instalación.")

        self.logger.info(f"Usando 'dpkg' para desinstalar '{package_name}'...")
        try:
            # Usamos -P para purgar los archivos de configuración también
            execute_command(["dpkg", "-P", package_name], self.logger, as_root=True)
            self.logger.success(f"El paquete '{package_name}' fue desinstalado y purgado.")
        except TPTError as e:
            raise TPTError(f"La desinstalación de '{package_name}' falló: {e}")

    def repair(self):
        """Ejecuta 'apt-get install -f' para arreglar dependencias rotas."""
        if not check_dependency("apt-get"):
            self.logger.warning("No se encuentra 'apt-get'. Omitiendo reparación de dependencias.")
            return

        try:
            execute_command(["apt-get", "install", "-f", "-y"], self.logger, as_root=True)
            self.logger.success("Reparación de dependencias completada.")
        except TPTError as e:
            self.logger.warning(f"La reparación de dependencias falló. Puede que necesites ejecutar 'sudo apt-get install -f' manualmente. Error: {e}")
