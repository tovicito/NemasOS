import os
from pathlib import Path
from .base_handler import BaseHandler
from ..utils.logger import Logger
from ..core.config import Configuracion
from ..utils.system import execute_command, check_dependency
from ..utils.exceptions import TPTError, CriticalTPTError

class ArchiveHandler(BaseHandler):
    """Manejador para instalar paquetes desde archivos comprimidos (.tar.gz, etc.)."""

    def __init__(self, pm, package_info: dict, config: Configuracion, logger: Logger, temp_path: Path, **kwargs):
        super().__init__(pm, package_info, config, logger)
        self.temp_path = temp_path
        if not check_dependency("tar"):
            raise CriticalTPTError("El comando 'tar' no se encuentra. Este manejador no puede funcionar sin él.")

    def _find_executable(self, extract_dir: Path) -> Path | None:
        """Intenta encontrar el ejecutable principal en el directorio extraído."""
        self.logger.info(f"Buscando ejecutable en {extract_dir}...")

        # Estrategia 1: Buscar un archivo con el mismo nombre que la app
        possible_exec = extract_dir / self.app_name
        if possible_exec.is_file() and os.access(possible_exec, os.X_OK):
            self.logger.info(f"Encontrado ejecutable por nombre: {possible_exec}")
            return possible_exec

        # Estrategia 2: Buscar en un subdirectorio 'bin'
        bin_dir = extract_dir / "bin"
        if bin_dir.is_dir():
            for item in bin_dir.iterdir():
                if item.is_file() and os.access(item, os.X_OK):
                    self.logger.info(f"Encontrado ejecutable en 'bin/': {item}")
                    return item

        # Estrategia 3: Buscar cualquier archivo ejecutable en la raíz del directorio
        for item in extract_dir.iterdir():
            if item.is_file() and os.access(item, os.X_OK):
                self.logger.info(f"Encontrado primer ejecutable disponible: {item}")
                return item

        self.logger.warning("No se pudo encontrar un ejecutable principal en el archivo.")
        return None

    def _get_tar_flags(self) -> str:
        """Determina los flags correctos para tar basado en la extensión del archivo."""
        filename = self.temp_path.name
        if filename.endswith(".tar.gz") or filename.endswith(".tgz"):
            return "xzf"
        elif filename.endswith(".tar.xz"):
            return "xJf"
        elif filename.endswith(".tar.bz2"):
            return "xjf"
        else:
            # Fallback para extensiones desconocidas, tar puede auto-detectar a menudo
            return "xf"

    def install(self) -> dict:
        """Extrae el archivo y configura el paquete."""
        extract_dir = self.config.DIR_OPT_ROOT / self.app_name
        self.logger.info(f"Extrayendo archivo en {extract_dir}...")

        try:
            # Limpiar y crear el directorio de extracción
            if extract_dir.exists():
                execute_command(["rm", "-rf", str(extract_dir)], self.logger, as_root=True)
            execute_command(["mkdir", "-p", str(extract_dir)], self.logger, as_root=True)

            # Extraer el contenido
            tar_flags = self._get_tar_flags()
            strip_components = self.package_info.get("metadata", {}).get("strip_components", 1)
            command = [
                "tar", tar_flags, str(self.temp_path),
                "-C", str(extract_dir),
                f"--strip-components={strip_components}"
            ]
            execute_command(command, self.logger, as_root=True)
        except TPTError as e:
            raise TPTError(f"No se pudo extraer el archivo: {e}")

        # Encontrar y enlazar el ejecutable
        executable_path = self._find_executable(extract_dir)
        symlink_path = None
        if executable_path:
            symlink_path = self.config.DIR_EJECUTABLES_ROOT / self.app_name
            self.logger.info(f"Creando enlace simbólico de {executable_path} a {symlink_path}")
            if symlink_path.exists() or symlink_path.is_symlink():
                execute_command(["rm", "-f", str(symlink_path)], self.logger, as_root=True)
            execute_command(["ln", "-s", str(executable_path), str(symlink_path)], self.logger, as_root=True)

        # Crear archivo .desktop
        desktop_file_path = self._create_desktop_file(symlink_path if symlink_path else extract_dir)

        self.logger.success(f"Paquete '{self.app_name}' instalado en {extract_dir}.")
        return {
            "handler": "ArchiveHandler",
            "install_path": str(extract_dir),
            "symlink_path": str(symlink_path) if symlink_path else None,
            "desktop_file": desktop_file_path
        }

    def uninstall(self, installation_details: dict):
        """Elimina el directorio extraído, el enlace y el .desktop."""
        install_path = installation_details.get("install_path")
        if install_path and Path(install_path).exists():
            self.logger.info(f"Eliminando directorio de instalación: {install_path}")
            try:
                execute_command(["rm", "-rf", install_path], self.logger, as_root=True)
            except TPTError as e:
                self.logger.warning(f"No se pudo eliminar {install_path}: {e}")

        symlink_path = installation_details.get("symlink_path")
        if symlink_path and (Path(symlink_path).exists() or Path(symlink_path).is_symlink()):
            self.logger.info(f"Eliminando enlace simbólico: {symlink_path}")
            try:
                execute_command(["rm", "-f", symlink_path], self.logger, as_root=True)
            except TPTError as e:
                self.logger.warning(f"No se pudo eliminar el enlace {symlink_path}: {e}")

        self._cleanup_desktop_file(installation_details)
        self.logger.success(f"Paquete '{self.app_name}' desinstalado.")
