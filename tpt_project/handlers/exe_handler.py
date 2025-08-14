import os
import logging
from pathlib import Path
from .base_handler import BaseHandler
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError, VerificationError

class ExeHandler(BaseHandler):
    """
    Manejador para instalar aplicaciones de Windows (.exe) usando Wine.
    Depende en gran medida de metadatos precisos en el manifiesto del paquete.
    """

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: logging.Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger)
        self.temp_path = temp_path
        if not check_dependency("wine"):
            raise CriticalTPTError("El comando 'wine' no se encuentra. TPT no puede gestionar aplicaciones .exe.")

        self.metadata = self.package_info.get("metadata", {})
        if "silent_install_flags" not in self.metadata or "executable_path_in_prefix" not in self.metadata:
            raise VerificationError("Los metadatos del paquete .exe son insuficientes. Se requieren 'silent_install_flags' y 'executable_path_in_prefix'.")

    def _get_wine_prefix(self) -> Path:
        """Devuelve la ruta al WINEPREFIX para esta aplicación."""
        # Usamos DIR_ESTADO que es seguro para escribir como usuario o root
        return self.config.DIR_ESTADO / "wine_prefixes" / self.app_name

    def install(self) -> dict:
        """Instala un .exe en un WINEPREFIX aislado."""
        wine_prefix = self._get_wine_prefix()
        self.logger.info(f"Creando y usando WINEPREFIX en: [dim]{wine_prefix}[/dim]")

        # Asegurarse de que el directorio de prefijos existe
        wine_prefix.parent.mkdir(parents=True, exist_ok=True)

        # Configurar el entorno para el comando de Wine
        wine_env = os.environ.copy()
        wine_env["WINEPREFIX"] = str(wine_prefix)
        wine_env["WINEDEBUG"] = "-all" # Suprimir la mayoría de los logs de Wine

        # Crear el prefijo de Wine (si no existe)
        execute_command(["wineboot", "-u"], self.logger, env=wine_env)

        self.logger.info("Ejecutando instalador .exe en modo silencioso...")
        install_command = ["wine", str(self.temp_path)] + self.metadata["silent_install_flags"]

        try:
            execute_command(install_command, self.logger, env=wine_env)
        except TPTError as e:
            raise TPTError(f"La instalación del .exe falló. Revisa los flags de instalación silenciosa. Error: {e}")

        # Crear el script lanzador
        launcher_path = self._create_launcher(wine_prefix)

        # Crear archivo .desktop
        desktop_file_path = self._create_desktop_file(launcher_path)

        self.logger.success(f"Aplicación '{self.app_name}' instalada en {wine_prefix}.")
        return {
            "handler": "ExeHandler",
            "wine_prefix": str(wine_prefix),
            "launcher_path": str(launcher_path),
            "desktop_file": desktop_file_path
        }

    def _create_launcher(self, wine_prefix: Path) -> Path:
        """Crea un script que lanza la aplicación de Windows."""
        launcher_path = self.config.DIR_EJECUTABLES_ROOT / self.app_name

        executable_in_prefix = self.metadata["executable_path_in_prefix"]
        full_exe_path = wine_prefix / executable_in_prefix

        self.logger.info(f"Creando script lanzador en {launcher_path}")

        script_content = (
            "#!/bin/sh\n"
            f"export WINEPREFIX='{wine_prefix}'\n"
            f"export WINEDEBUG='-all'\n"
            f"wine \"{full_exe_path}\" \"$@\""
        )

        # Escribir el script lanzador (requiere root)
        try:
            command = ["tee", str(launcher_path)]
            execute_command(command, self.logger, as_root=True, input=script_content)
            execute_command(["chmod", "+x", str(launcher_path)], self.logger, as_root=True)
            return launcher_path
        except TPTError as e:
            self.logger.error(f"No se pudo crear el script lanzador: {e}")
            # Continuar sin lanzador es posible, pero la app no estará en el PATH
            return None

    def uninstall(self, installation_details: dict):
        """Desinstala la aplicación eliminando su WINEPREFIX."""
        wine_prefix_str = installation_details.get("wine_prefix")
        if not wine_prefix_str:
            raise TPTError("No se puede desinstalar: falta 'wine_prefix' en los detalles.")

        wine_prefix = Path(wine_prefix_str)
        if wine_prefix.exists():
            self.logger.info(f"Eliminando WINEPREFIX completo: {wine_prefix}")
            # La eliminación del prefijo debe ser como el usuario que lo creó
            as_root = (str(wine_prefix).startswith("/var/lib"))
            try:
                execute_command(["rm", "-rf", str(wine_prefix)], self.logger, as_root=as_root)
            except TPTError as e:
                self.logger.warning(f"No se pudo eliminar el WINEPREFIX: {e}")

        launcher_path_str = installation_details.get("launcher_path")
        if launcher_path_str and Path(launcher_path_str).exists():
            try:
                execute_command(["rm", "-f", launcher_path_str], self.logger, as_root=True)
            except TPTError as e:
                self.logger.warning(f"No se pudo eliminar el lanzador: {e}")

        self._cleanup_desktop_file(installation_details)
        self.logger.success(f"Aplicación Windows '{self.app_name}' desinstalada.")
