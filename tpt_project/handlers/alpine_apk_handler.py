import logging
from pathlib import Path
from .base_handler import BaseHandler
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError

class AlpineApkHandler(BaseHandler):
    """
    Manejador para paquetes .apk de Alpine Linux.
    Este manejador solo funciona si TPT se ejecuta en Alpine Linux.
    """

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: logging.Logger, temp_path: Path = None, **kwargs):
        super().__init__(pm, package_info, config, logger)
        self.temp_path = temp_path

        if not Path("/etc/alpine-release").exists():
            raise CriticalTPTError("Este sistema no es Alpine Linux. El manejador 'AlpineApkHandler' no puede operar.")
        if not check_dependency("apk"):
            raise CriticalTPTError("El comando 'apk' no se encuentra. No se pueden gestionar paquetes de Alpine.")

        # Para este manejador, el nombre del paquete es clave.
        self.package_name = self.package_info.get("package_name", self.app_name)

    def install(self) -> dict:
        """Instala un paquete usando el comando 'apk'."""

        if self.temp_path:
            # Instalar desde un archivo .apk local
            self.logger.info(f"Instalando paquete local de Alpine: {self.temp_path}")
            # Se requiere --allow-untrusted para instalar APKs locales
            command = ["apk", "add", "--allow-untrusted", str(self.temp_path)]
        else:
            # Instalar desde el repositorio de Alpine
            self.logger.info(f"Instalando paquete de Alpine desde el repositorio: {self.package_name}")
            command = ["apk", "add", self.package_name]

        try:
            execute_command(command, self.logger, as_root=True)
            self.logger.success(f"Paquete de Alpine '{self.package_name}' instalado con éxito.")
        except TPTError as e:
            raise TPTError(f"No se pudo instalar el paquete de Alpine '{self.package_name}': {e}")

        return {
            "handler": "AlpineApkHandler",
            "package_name": self.package_name
        }

    def uninstall(self, installation_details: dict):
        """Desinstala un paquete usando el comando 'apk'."""
        package_to_uninstall = installation_details.get("package_name")
        if not package_to_uninstall:
            raise TPTError("No se puede desinstalar: falta 'package_name' en los detalles de instalación.")

        self.logger.info(f"Desinstalando paquete de Alpine: {package_to_uninstall}")
        command = ["apk", "del", package_to_uninstall]

        try:
            execute_command(command, self.logger, as_root=True)
            self.logger.success(f"Paquete de Alpine '{package_to_uninstall}' desinstalado.")
        except TPTError as e:
            raise TPTError(f"No se pudo desinstalar el paquete de Alpine '{package_to_uninstall}': {e}")
