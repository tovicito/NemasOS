from pathlib import Path
from .base_handler import BaseHandler
from .deb_handler import DebHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError

class DebXzHandler(BaseHandler):
    """
    Manejador para paquetes .deb comprimidos con xz.
    Actúa como un pre-procesador para DebHandler.
    """

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger, **kwargs)
        self.temp_path = temp_path
        if not check_dependency("unxz"):
            raise CriticalTPTError("El comando 'unxz' no se encuentra. TPT no puede gestionar archivos .deb.xz.")

    def install(self) -> dict:
        """Descomprime el .deb.xz y luego lo pasa al DebHandler."""

        decompressed_deb_path = self.temp_path.with_suffix('') # Quita la extensión .xz
        self.logger.info(f"Descomprimiendo {self.temp_path} a {decompressed_deb_path}...")

        try:
            # unxz por defecto borra el original, lo cual está bien para un fichero temporal
            execute_command(["unxz", str(self.temp_path)], self.logger)
        except TPTError as e:
            raise TPTError(f"No se pudo descomprimir el archivo .deb.xz: {e}")

        self.logger.info("Descompresión completa. Pasando al manejador de .deb...")

        # Ahora, instanciar y usar el DebHandler con el archivo descomprimido
        deb_handler = DebHandler(self.pm, self.package_info, self.config, self.logger, temp_path=decompressed_deb_path)

        # La instalación real la hace el DebHandler
        installation_details = deb_handler.install()

        # La desinstalación también la gestionará el DebHandler, así que devolvemos sus detalles
        return installation_details

    def uninstall(self, installation_details: dict):
        """La desinstalación la maneja directamente DebHandler, este método no debería ser llamado."""
        self.logger.error("El método de desinstalación de DebXzHandler no debe ser invocado directamente.")
        raise NotImplementedError("La desinstalación es manejada por el DebHandler a través de los detalles guardados en la BD.")
