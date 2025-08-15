import sys
import traceback
from datetime import datetime

try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.traceback import Traceback
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

class Logger:
    """Un registrador moderno para TPT que usa 'rich' para una salida bonita."""

    def __init__(self, config):
        self.log_file_path = config.ARCHIVO_LOG
        self.log_levels = {"DEBUG": 0, "INFO": 1, "SUCCESS": 2, "WARNING": 3, "ERROR": 4, "CRITICAL": 5}
        self.current_log_level = self.log_levels["INFO"]

        if not HAS_RICH:
            self.user_console = None # No console if rich is not there
        else:
            custom_theme = Theme({
                "info": "dim cyan",
                "success": "bold green",
                "warning": "yellow",
                "error": "bold red",
                "critical": "bold white on red",
                "debug": "dim green",
            })
            self.user_console = Console(theme=custom_theme)

    def _log(self, level_name: str, message: str, exc_info=False):
        level_value = self.log_levels.get(level_name.upper(), 1)
        if level_value < self.current_log_level:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level_name.upper()}] {message}"

        # Escribir en el fichero de log
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
                if exc_info:
                    traceback.print_exc(file=f)
        except IOError as e:
            print(f"CRITICAL: Could not write to log file {self.log_file_path}: {e}", file=sys.stderr)

        # Escribir en la consola si rich está disponible
        if self.user_console:
            style = level_name.lower()
            # Rich console's log method handles presentation
            self.user_console.log(message, style=style)
            if exc_info:
                self.user_console.print_exception(show_locals=True)
        else: # Fallback sin rich
            print(log_entry, file=sys.stderr if level_value >= self.log_levels["ERROR"] else sys.stdout)
            if exc_info:
                traceback.print_exc(file=sys.stderr)

    def debug(self, message: str, exc_info=False): self._log("DEBUG", message, exc_info)
    def info(self, message: str, exc_info=False): self._log("INFO", message, exc_info)
    def success(self, message: str, exc_info=False): self._log("SUCCESS", message, exc_info)
    def warning(self, message: str, exc_info=False): self._log("WARNING", message, exc_info)
    def error(self, message: str, exc_info=False): self._log("ERROR", message, exc_info)
    def critical(self, message: str, exc_info=False): self._log("CRITICAL", message, exc_info)
