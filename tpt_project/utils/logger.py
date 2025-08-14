import logging
from pathlib import Path

try:
    from rich.logging import RichHandler
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Añadir un nuevo nivel de log para 'SUCCESS'
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)
logging.Logger.success = success

def setup_logger(config):
    """Configura y devuelve el logger principal de TPT."""

    log = logging.getLogger("tpt")
    log.setLevel(logging.DEBUG) # Capturar todos los niveles, los manejadores deciden qué mostrar

    # Evitar añadir manejadores duplicados si la función se llama más de una vez
    if log.hasHandlers():
        log.handlers.clear()

    # Formateador para el fichero de log
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Manejador para el fichero de log
    file_handler = logging.FileHandler(config.ARCHIVO_LOG, mode='a', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG) # Escribir todo al fichero
    log.addHandler(file_handler)

    # Manejador para la consola (usando Rich si está disponible)
    if HAS_RICH:
        rich_handler = RichHandler(
            show_time=False,
            rich_tracebacks=True,
            markup=True,
            keywords=RichHandler.KEYWORDS + ["TPT", "AADPO"]
        )
        rich_handler.setLevel(logging.INFO) # No mostrar DEBUG en la consola por defecto
        log.addHandler(rich_handler)
    else:
        # Fallback a un manejador de consola estándar si Rich no está
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(file_formatter)
        stream_handler.setLevel(logging.INFO)
        log.addHandler(stream_handler)

    return log
