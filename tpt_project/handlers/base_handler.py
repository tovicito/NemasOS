from abc import ABC, abstractmethod
from pathlib import Path
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command
from ..utils.exceptions import TPTError

class BaseHandler(ABC):
    """
    Clase base abstracta para todos los manejadores de tipos de paquete.
    Define la interfaz común que todos los manejadores deben implementar.
    """
    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, **kwargs):
        self.pm = pm
        self.package_info = package_info
        self.config = config
        self.logger = logger
        self.app_name = self.package_info.get('name')

    @abstractmethod
    def install(self) -> dict:
        """
        Instala el paquete.
        Debe ser implementado por cada subclase.

        Returns:
            Un diccionario con los detalles de la instalación para guardar en la base de datos.
        """
        pass

    @abstractmethod
    def uninstall(self, installation_details: dict):
        """
        Desinstala el paquete usando los detalles de la instalación.
        Debe ser implementado por cada subclase.

        Args:
            installation_details: El diccionario guardado en la base de datos durante la instalación.
        """
        pass

    def _create_desktop_file(self, executable_path: Path) -> str | None:
        """
        Crea un archivo .desktop para la integración con el entorno de escritorio.
        """
        if not self.package_info.get("metadata"):
            self.logger.info("No hay metadatos para crear el archivo .desktop. Omitiendo.")
            return None

        metadata = self.package_info["metadata"]
        desktop_filename = f"{self.app_name}.desktop"
        desktop_filepath = self.config.DIR_APLICACIONES_ROOT / desktop_filename

        # Asegurarse de que el directorio de aplicaciones exista (requiere root)
        try:
            execute_command(["mkdir", "-p", str(self.config.DIR_APLICACIONES_ROOT)], self.logger, as_root=True)
        except TPTError as e:
            self.logger.error(f"No se pudo crear el directorio de aplicaciones. ¿Faltan permisos? Error: {e}")
            return None

        self.logger.info(f"Creando archivo .desktop en {desktop_filepath}")

        # Usar .get() para todos los campos para evitar KeyErrors
        content = (
            "[Desktop Entry]\n"
            "Version=1.0\n"
            "Type=Application\n"
            f"Name={self.app_name}\n"
            f"Comment={self.package_info.get('description', '')}\n"
            f"Exec={executable_path}\n"
            f"Icon={metadata.get('icon', 'application-x-executable')}\n"
            f"Terminal={'true' if str(metadata.get('terminal', 'false')).lower() == 'true' else 'false'}\n"
            f"Categories={metadata.get('categories', 'Utility;')}\n"
        )

        # Escribir el archivo .desktop requiere permisos de root, así que lo hacemos con un truco de `tee`
        try:
            command = ["tee", str(desktop_filepath)]
            # Usamos `input` para pasar el contenido del .desktop a través de stdin
            execute_command(command, self.logger, as_root=True, input=content)
            execute_command(["chmod", "644", str(desktop_filepath)], self.logger, as_root=True)
            return str(desktop_filepath)
        except TPTError as e:
            self.logger.error(f"No se pudo crear el archivo .desktop: {e}")
            return None

    def _cleanup_desktop_file(self, installation_details: dict):
        """
        Elimina un archivo .desktop si fue creado durante la instalación.
        """
        if 'desktop_file' in installation_details and installation_details['desktop_file']:
            desktop_file = Path(installation_details['desktop_file'])
            if desktop_file.exists():
                self.logger.info(f"Eliminando archivo .desktop: {desktop_file}")
                try:
                    execute_command(["rm", "-f", str(desktop_file)], self.logger, as_root=True)
                except TPTError as e:
                    self.logger.warning(f"No se pudo eliminar el archivo .desktop: {e}")
