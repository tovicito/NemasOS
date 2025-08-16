import logging
import sys
from datetime import datetime

try:
    from rich.logging import RichHandler
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Un mapa para convertir nuestros niveles de log a los de logging estándar
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "SUCCESS": logging.INFO + 1, # Nivel personalizado
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

class TPTLogger:
    """
    Un registrador para TPT que se integra con el módulo logging de Python
    y opcionalmente usa 'rich' para una salida bonita.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TPTLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, config, level=logging.INFO):
        # Evitar re-inicialización si la instancia ya existe
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.logger = logging.getLogger("tpt")
        self.logger.setLevel(level)

        # Limpiar manejadores existentes para evitar duplicados
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Configurar el manejador de archivo
        file_handler = logging.FileHandler(config.ARCHIVO_LOG, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Configurar el manejador de consola (rich o estándar)
        if HAS_RICH:
            console_handler = RichHandler(rich_tracebacks=True, show_path=False)
            # No queremos el nombre del logger ni la hora en la consola de rich
            console_handler.setFormatter(logging.Formatter('%(message)s'))
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            # Filtrar para que solo muestre INFO y superior en stdout
            console_handler.addFilter(lambda record: record.levelno >= logging.INFO)

        self.logger.addHandler(console_handler)

        # Nivel de log personalizado para SUCCESS
        logging.addLevelName(LOG_LEVEL_MAP["SUCCESS"], "SUCCESS")
        def success(self, message, *args, **kws):
            if self.isEnabledFor(LOG_LEVEL_MAP["SUCCESS"]):
                self._log(LOG_LEVEL_MAP["SUCCESS"], message, args, **kws)
        logging.Logger.success = success

        self._initialized = True

    def get_logger(self):
        return self.logger
