from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError, VerificationError

class FlatpakHandler(BaseHandler):
    """
    Manejador para instalar y desinstalar aplicaciones Flatpak.
    Este manejador no descarga un archivo, sino que interactúa con el demonio de Flatpak.
    """

    def __init__(self, package_info: dict, config: Configuracion, logger: Logger, **kwargs):
        super().__init__(package_info, config, logger)
        if not check_dependency("flatpak"):
            raise CriticalTPTError("El comando 'flatpak' no se encuentra. TPT no puede gestionar aplicaciones Flatpak.")

        # Para Flatpak, el 'app_id' es crucial
        if "app_id" not in self.package_info:
            raise VerificationError("La información del paquete Flatpak es inválida: falta el 'app_id'.")
        self.app_id = self.package_info["app_id"]
        # El remote es opcional, Flatpak puede encontrarlo si está configurado
        self.remote = self.package_info.get("remote", "flathub") # Default a flathub si no se especifica

    def install(self) -> dict:
        """Instala una aplicación Flatpak usando su app_id."""
        self.logger.info(f"Instalando Flatpak [bold cyan]{self.app_id}[/bold cyan] desde el remote [bold cyan]{self.remote}[/bold cyan]...")

        # Usamos --user para instalarlo para el usuario actual sin necesidad de sudo
        # Usamos --noninteractive para evitar cualquier pregunta
        command = [
            "flatpak", "install", "--user", "--noninteractive",
            self.remote,
            self.app_id
        ]

        try:
            execute_command(command, self.logger)
            self.logger.success(f"Aplicación Flatpak '{self.app_id}' instalada correctamente.")
        except TPTError as e:
            self.logger.error(f"La instalación de Flatpak falló. Comprueba que el remote '{self.remote}' está añadido (`flatpak remotes`).")
            raise TPTError(f"No se pudo instalar la aplicación Flatpak '{self.app_id}': {e}")

        return {
            "handler": "FlatpakHandler",
            "app_id": self.app_id
        }

    def uninstall(self, installation_details: dict):
        """Desinstala una aplicación Flatpak usando su app_id."""
        app_id_to_uninstall = installation_details.get("app_id")
        if not app_id_to_uninstall:
            raise TPTError("No se puede desinstalar: falta 'app_id' en los detalles de instalación de Flatpak.")

        self.logger.info(f"Desinstalando Flatpak [bold cyan]{app_id_to_uninstall}[/bold cyan]...")

        command = [
            "flatpak", "uninstall", "--user", "--noninteractive",
            app_id_to_uninstall
        ]

        try:
            execute_command(command, self.logger)
            self.logger.success(f"Aplicación Flatpak '{app_id_to_uninstall}' desinstalada.")
        except TPTError as e:
            raise TPTError(f"No se pudo desinstalar la aplicación Flatpak '{app_id_to_uninstall}': {e}")
