from pathlib import Path
from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError
import logging

class RpmHandler(BaseHandler):
    """
    Manejador para instalar y desinstalar paquetes .rpm.
    Prioritiza el uso de gestores de alto nivel como DNF o Zypper.
    """

    def __init__(self, pm, package_info: dict, config, logger: logging.Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger, **kwargs)
        self.temp_path = temp_path
        self.pm_tool = self._detect_package_manager()
        if not self.pm_tool:
            raise CriticalTPTError("No se encontró un gestor de paquetes RPM compatible (dnf, zypper, rpm).")

    def _detect_package_manager(self) -> str | None:
        """Detecta el mejor gestor de paquetes RPM disponible."""
        if check_dependency("dnf"):
            self.logger.info("Detectado 'dnf' como gestor de paquetes.")
            return "dnf"
        if check_dependency("zypper"):
            self.logger.info("Detectado 'zypper' como gestor de paquetes.")
            return "zypper"
        if check_dependency("rpm"):
            self.logger.warning("Usando 'rpm' como fallback. Las dependencias no se resolverán automáticamente.")
            return "rpm"
        return None

    def _get_package_name_from_rpm(self) -> str:
        """Extrae el nombre canónico del paquete desde el archivo RPM."""
        try:
            # rpm -q --qf '%{NAME}' -p /path/to/file.rpm
            command = ["rpm", "-q", "--queryformat", "%{NAME}", "-p", str(self.temp_path)]
            result = execute_command(command, self.logger)
            package_name = result.stdout.strip()
            if not package_name:
                raise TPTError("La salida del comando rpm para obtener el nombre estaba vacía.")
            self.logger.info(f"Nombre de paquete extraído del RPM: {package_name}")
            return package_name
        except TPTError as e:
            self.logger.error(f"No se pudo extraer el nombre del paquete del archivo RPM. Usando el nombre de la app como fallback. Error: {e}")
            return self.app_name

    def install(self) -> dict:
        """Instala el paquete .rpm usando el mejor gestor de paquetes disponible."""
        self.logger.info(f"Instalando RPM {self.temp_path} usando '{self.pm_tool}'...")

        if self.pm_tool == "dnf":
            command = ["dnf", "install", "-y", str(self.temp_path)]
        elif self.pm_tool == "zypper":
            command = ["zypper", "--non-interactive", "install", str(self.temp_path)]
        else: # rpm
            command = ["rpm", "-i", str(self.temp_path)]

        try:
            execute_command(command, self.logger, as_root=True)
            package_name = self._get_package_name_from_rpm()
            self.logger.info(f"Paquete RPM '{package_name}' instalado con éxito.")
        except TPTError as e:
            raise TPTError(f"La instalación del RPM falló: {e}")

        return {
            "handler": "RpmHandler",
            "package_name": package_name
        }

    def uninstall(self, installation_details: dict):
        """Desinstala un paquete RPM usando el gestor de paquetes."""
        package_name = installation_details.get("package_name")
        if not package_name:
            raise TPTError("No se puede desinstalar: falta 'package_name' en los detalles de instalación.")

        self.logger.info(f"Desinstalando RPM '{package_name}' usando '{self.pm_tool}'...")

        if self.pm_tool == "dnf":
            command = ["dnf", "remove", "-y", package_name]
        elif self.pm_tool == "zypper":
            command = ["zypper", "--non-interactive", "remove", package_name]
        else: # rpm
            command = ["rpm", "-e", package_name]

        try:
            execute_command(command, self.logger, as_root=True)
            self.logger.info(f"Paquete RPM '{package_name}' desinstalado.")
        except TPTError as e:
            raise TPTError(f"La desinstalación del RPM '{package_name}' falló: {e}")
