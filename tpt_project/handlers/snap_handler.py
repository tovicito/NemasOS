from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError, VerificationError

class SnapHandler(BaseHandler):
    """
    Manejador para instalar y desinstalar paquetes Snap.
    Este manejador interactúa con el demonio snapd.
    """

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, **kwargs):
        super().__init__(pm, package_info, config, logger)
        if not check_dependency("snap"):
            raise CriticalTPTError("El comando 'snap' no se encuentra. TPT no puede gestionar aplicaciones Snap.")

        if "snap_name" not in self.package_info:
            raise VerificationError("La información del paquete Snap es inválida: falta el 'snap_name'.")

        self.snap_name = self.package_info["snap_name"]
        self.channel = self.package_info.get("channel")
        self.classic = self.package_info.get("classic", False)

    def install(self) -> dict:
        """Instala un paquete Snap."""
        self.logger.info(f"Instalando Snap [bold cyan]{self.snap_name}[/bold cyan]...")

        command = ["snap", "install", self.snap_name]

        if self.channel:
            command.extend(["--channel", self.channel])
            self.logger.info(f"Usando el canal: {self.channel}")

        if self.classic:
            command.append("--classic")
            self.logger.warning("Este paquete Snap requiere confinamiento clásico, lo que le da más acceso al sistema.")

        try:
            # La instalación de Snaps requiere privilegios de root
            execute_command(command, self.logger, as_root=True)
            self.logger.success(f"Snap '{self.snap_name}' instalado correctamente.")
        except TPTError as e:
            raise TPTError(f"No se pudo instalar el Snap '{self.snap_name}': {e}")

        return {
            "handler": "SnapHandler",
            "snap_name": self.snap_name
        }

    def uninstall(self, installation_details: dict):
        """Desinstala un paquete Snap."""
        snap_to_uninstall = installation_details.get("snap_name")
        if not snap_to_uninstall:
            raise TPTError("No se puede desinstalar: falta 'snap_name' en los detalles de instalación de Snap.")

        self.logger.info(f"Desinstalando Snap [bold cyan]{snap_to_uninstall}[/bold cyan]...")

        command = ["snap", "remove", snap_to_uninstall]

        try:
            execute_command(command, self.logger, as_root=True)
            self.logger.success(f"Snap '{snap_to_uninstall}' desinstalado.")
        except TPTError as e:
            raise TPTError(f"No se pudo desinstalar el Snap '{snap_to_uninstall}': {e}")
