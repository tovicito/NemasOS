import os
import shutil
import subprocess
import logging
from .exceptions import SystemCommandError

def execute_command(command: list[str], logger: logging.Logger, as_root: bool = False, **kwargs) -> subprocess.CompletedProcess:
    """
    Ejecuta un comando del sistema, manejando la elevación de privilegios (sudo) y registrando la salida.

    Args:
        command: El comando a ejecutar como una lista de strings.
        logger: La instancia del registrador para la salida.
        as_root: Si es True, ejecuta el comando con 'sudo'.
        **kwargs: Argumentos adicionales para subprocess.run.

    Returns:
        El objeto subprocess.CompletedProcess en caso de éxito.

    Raises:
        SystemCommandError: Si el comando devuelve un código de salida distinto de cero.
    """
    if as_root and os.geteuid() != 0:
        command.insert(0, "sudo")

    logger.debug(f"Ejecutando comando: {' '.join(command)}")

    try:
        # Forzamos text=True y encoding='utf-8' para una salida consistente
        kwargs.setdefault('text', True)
        kwargs.setdefault('encoding', 'utf-8')
        kwargs.setdefault('capture_output', True)

        result = subprocess.run(command, check=True, **kwargs)

        if result.stdout:
            logger.debug(f"Salida de '{command[0]}':\n{result.stdout.strip()}")
        if result.stderr:
            # Algunas herramientas (como apt) usan stderr para información de estado, así que lo registramos como aviso
            logger.warning(f"Salida de error de '{command[0]}':\n{result.stderr.strip()}")

        return result

    except FileNotFoundError:
        logger.error(f"Comando no encontrado: {command[0]}. ¿Está instalado y en el PATH?")
        raise SystemCommandError(command, f"Comando no encontrado: {command[0]}")
    except subprocess.CalledProcessError as e:
        logger.error(f"El comando falló: {' '.join(command)}")
        logger.error(f"Stderr: {e.stderr.strip()}")
        raise SystemCommandError(command, e.stderr)
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado al ejecutar el comando: {' '.join(command)}")
        logger.error(f"Error: {e}")
        raise SystemCommandError(command, str(e))

def check_dependency(name: str) -> str | None:
    """
    Comprueba si una dependencia (comando) está disponible en el PATH del sistema.

    Args:
        name: El nombre del comando a comprobar (p. ej., 'dpkg', 'flatpak').

    Returns:
        La ruta completa al ejecutable si se encuentra, de lo contrario None.
    """
    return shutil.which(name)
