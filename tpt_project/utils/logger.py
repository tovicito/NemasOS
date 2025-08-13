import sys
import traceback
from datetime import datetime
from pathlib import Path

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

        if not HAS_RICH:
            self.console = self._create_fallback_console()
            self.print = self.console.print
            self.log = self.console.log
        else:
            custom_theme = Theme({
                "info": "dim cyan",
                "warning": "yellow",
                "error": "bold red",
                "critical": "bold white on red",
                "debug": "dim green",
                "success": "bold green"
            })

            # Consola para la salida a fichero
            self.log_file = open(self.log_file_path, "a", encoding="utf-8")
            self.file_console = Console(
                file=self.log_file,
                record=True,
                log_time_format="[%Y-%m-%d %H:%M:%S.%f]",
                width=120,
                no_color=True
            )

            # Consola para la salida a la terminal del usuario
            self.user_console = Console(theme=custom_theme)
            self.print = self.user_console.print
            self.log = self.user_console.log

    def _log_to_file(self, level: str, message: str, exc_info=False):
        if not hasattr(self, 'file_console'): return

        log_message = f"[{level.upper()}] {message}"
        if exc_info:
            log_message += "\n" + traceback.format_exc()
        self.file_console.log(log_message)
        self.log_file.flush()

    def info(self, message: str):
        self.log(f"[INFO] {message}", style="info")
        self._log_to_file("INFO", message)

    def success(self, message: str):
        self.log(f"[ÉXITO] {message}", style="success")
        self._log_to_file("SUCCESS", message)

    def warning(self, message: str):
        self.log(f"[AVISO] {message}", style="warning")
        self._log_to_file("WARNING", message)

    def error(self, message: str, exc_info=False):
        self.log(f"[ERROR] {message}", style="error")
        if exc_info and HAS_RICH:
            self.user_console.print(Traceback(show_locals=True))
        self._log_to_file("ERROR", message, exc_info=exc_info)

    def critical(self, message: str, exc_info=True):
        self.log(f"[CRÍTICO] {message}", style="critical")
        if exc_info and HAS_RICH:
            self.user_console.print(Traceback(show_locals=True))
        self._log_to_file("CRITICAL", message, exc_info=exc_info)

    def debug(self, message: str):
        # El debug solo va a fichero, no a la consola del usuario por defecto
        self._log_to_file("DEBUG", message)

    def _create_fallback_console(self):
        """Crea una consola de reemplazo si 'rich' no está instalado."""
        class FallbackConsole:
            def print(self, msg, **kwargs):
                print(msg)
            def log(self, msg, **kwargs):
                print(msg)
        return FallbackConsole()

    def __del__(self):
        if hasattr(self, 'log_file'):
            self.log_file.close()
