from pathlib import Path
from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError

class PowershellHandler(BaseHandler):
    """Manejador para instalar y ejecutar scripts de PowerShell (.ps1) como aplicaciones."""

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger)
        self.temp_path = temp_path
        if not check_dependency("pwsh"):
            raise CriticalTPTError("El comando 'pwsh' no se encuentra. TPT no puede gestionar scripts de PowerShell.")

    def install(self) -> dict:
        """Instala un script de PowerShell y crea un lanzador para él."""

        install_dir = self.config.DIR_OPT_ROOT / "tpt_ps1_scripts" / self.app_name
        install_path = install_dir / self.temp_path.name
        launcher_path = self.config.DIR_EJECUTABLES_ROOT / self.app_name

        self.logger.info(f"Instalando script de PowerShell en {install_path}...")

        try:
            # Crear el directorio de instalación y mover el script
            execute_command(["mkdir", "-p", str(install_dir)], self.logger, as_root=True)
            execute_command(["mv", str(self.temp_path), str(install_path)], self.logger, as_root=True)

            # Crear el script lanzador
            self.logger.info(f"Creando lanzador en {launcher_path}")
            launcher_content = (
                "#!/bin/sh\n"
                f"pwsh \"{install_path}\" \"$@\"\n"
            )
            command = ["tee", str(launcher_path)]
            execute_command(command, self.logger, as_root=True, input=launcher_content)
            execute_command(["chmod", "+x", str(launcher_path)], self.logger, as_root=True)

        except TPTError as e:
            raise TPTError(f"No se pudo instalar el script de PowerShell: {e}")

        # Crear archivo .desktop
        desktop_file_path = self._create_desktop_file(launcher_path)

        self.logger.success(f"Script de PowerShell '{self.app_name}' instalado correctamente.")
        return {
            "handler": "PowershellHandler",
            "install_path": str(install_path),
            "launcher_path": str(launcher_path),
            "desktop_file": desktop_file_path
        }

    def uninstall(self, installation_details: dict):
        """Elimina el script de PowerShell, su lanzador y su .desktop."""

        install_path_str = installation_details.get("install_path")
        if install_path_str:
            # Eliminar el directorio padre del script para limpiar todo
            install_dir = Path(install_path_str).parent
            if install_dir.exists():
                self.logger.info(f"Eliminando directorio de script: {install_dir}")
                try:
                    execute_command(["rm", "-rf", str(install_dir)], self.logger, as_root=True)
                except TPTError as e:
                    self.logger.warning(f"No se pudo eliminar el directorio del script: {e}")

        launcher_path_str = installation_details.get("launcher_path")
        if launcher_path_str and Path(launcher_path_str).exists():
            self.logger.info(f"Eliminando lanzador: {launcher_path_str}")
            try:
                execute_command(["rm", "-f", launcher_path_str], self.logger, as_root=True)
            except TPTError as e:
                self.logger.warning(f"No se pudo eliminar el lanzador: {e}")

        self._cleanup_desktop_file(installation_details)
        self.logger.success(f"Script de PowerShell '{self.app_name}' desinstalado.")
