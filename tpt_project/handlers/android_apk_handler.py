import re
from pathlib import Path
from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError, VerificationError

class AndroidApkHandler(BaseHandler):
    """
    Manejador para aplicaciones .apk de Android a través de Waydroid.
    ADVERTENCIA: Esta es una característica avanzada y requiere que el usuario
    tenga un entorno Waydroid completamente funcional.
    """

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger, **kwargs)
        self.temp_path = temp_path

        if not check_dependency("waydroid"):
            raise CriticalTPTError("El comando 'waydroid' no se encuentra. TPT no puede gestionar APKs de Android sin un entorno Waydroid funcional.")
        if not check_dependency("aapt"):
            # aapt es parte de las Android Build Tools, necesario para inspeccionar los APKs.
            raise CriticalTPTError("El comando 'aapt' no se encuentra. TPT necesita 'aapt' (de las Android Build Tools) para extraer información de los APKs.")

    def _get_app_id_from_apk(self) -> str:
        """Extrae el ID del paquete (ej: com.spotify.music) de un archivo APK usando aapt."""
        self.logger.info(f"Inspeccionando {self.temp_path} para obtener el ID de la aplicación...")
        try:
            command = ["aapt", "dump", "badging", str(self.temp_path)]
            result = execute_command(command, self.logger)

            match = re.search(r"package: name='([^']+)'", result.stdout)
            if match:
                app_id = match.group(1)
                self.logger.info(f"ID de la aplicación extraído: [bold cyan]{app_id}[/bold cyan]")
                return app_id
            else:
                raise VerificationError("No se pudo encontrar el 'package name' en la salida de aapt. El APK puede ser inválido.")
        except TPTError as e:
            raise VerificationError(f"Falló la inspección del APK con aapt: {e}")

    def install(self) -> dict:
        """Instala un APK de Android usando Waydroid."""
        app_id = self._get_app_id_from_apk()

        self.logger.info(f"Instalando APK '{app_id}' en Waydroid...")
        command = ["waydroid", "app", "install", str(self.temp_path)]

        try:
            # Waydroid no necesita sudo para instalar apps
            execute_command(command, self.logger)
            self.logger.success(f"Aplicación Android '{app_id}' enviada a Waydroid para su instalación.")
            self.logger.info("Waydroid gestionará la instalación en segundo plano. Puede tardar unos momentos en aparecer.")
        except TPTError as e:
            raise TPTError(f"No se pudo instalar el APK en Waydroid: {e}")

        return {
            "handler": "AndroidApkHandler",
            "app_id": app_id
        }

    def uninstall(self, installation_details: dict):
        """Desinstala una aplicación de Android de Waydroid."""
        app_id_to_uninstall = installation_details.get("app_id")
        if not app_id_to_uninstall:
            raise TPTError("No se puede desinstalar: falta 'app_id' en los detalles de instalación.")

        self.logger.info(f"Desinstalando aplicación Android '{app_id_to_uninstall}' de Waydroid...")
        command = ["waydroid", "app", "remove", app_id_to_uninstall]

        try:
            execute_command(command, self.logger)
            self.logger.success(f"Aplicación Android '{app_id_to_uninstall}' desinstalada de Waydroid.")
        except TPTError as e:
            raise TPTError(f"No se pudo desinstalar la aplicación de Waydroid: {e}")
