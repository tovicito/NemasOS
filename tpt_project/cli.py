import argparse
import sys
import logging
from .core.package_manager import PackageManager
from .utils.exceptions import TPTError

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.traceback import Traceback
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

class CLI:
    """Maneja toda la interacción con el usuario a través de la línea de comandos."""

    def __init__(self, pm: PackageManager, logger: logging.Logger):
        self.pm = pm
        self.logger = logger
        self.console = Console() if HAS_RICH else None

    def run(self, argv=None):
        """Punto de entrada principal para la CLI."""
        parser = self._create_parser()
        args = parser.parse_args(argv)

        try:
            if hasattr(args, 'handler'):
                args.handler(args)
            else:
                parser.print_help()
        except TPTError as e:
            self.logger.error(e.message)
            sys.exit(1)
        except KeyboardInterrupt:
            self.logger.warning("\nOperación cancelada por el usuario.")
            sys.exit(130)
        except Exception as e:
            self.logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
            if self.console:
                self.console.print_exception(show_locals=True)
            sys.exit(1)

    def _create_parser(self):
        """Configura argparse para todos los comandos."""
        parser = argparse.ArgumentParser(
            prog="tpt",
            description=Panel("TPT - La Herramienta de Paquetes Total", title="[bold green]TPT v3.0[/bold green]", expand=False)
        )
        parser.add_argument("-v", "--version", action="version", version="%(prog)s 3.0.0")
        subparsers = parser.add_subparsers(title="Comandos disponibles", dest="command")

        # Comando 'buscar'
        p_search = subparsers.add_parser("buscar", help="Buscar un paquete en los repositorios.")
        p_search.add_argument("termino", help="Término de búsqueda.")
        p_search.set_defaults(handler=self._handle_search)

        # Comando 'instalar'
        p_install = subparsers.add_parser("instalar", help="Instalar uno o más paquetes.")
        p_install.add_argument("nombres_paquete", nargs='+', help="Nombre(s) del(los) paquete(s) a instalar.")
        p_install.set_defaults(handler=self._handle_install)

        # Comando 'desinstalar'
        p_uninstall = subparsers.add_parser("desinstalar", help="Desinstalar uno o más paquetes.")
        p_uninstall.add_argument("nombres_paquete", nargs='+', help="Nombre(s) del(los) paquete(s) a desinstalar.")
        p_uninstall.set_defaults(handler=self._handle_uninstall)

        # Comando 'listar'
        p_list = subparsers.add_parser("listar", help="Listar todos los paquetes instalados por TPT.")
        p_list.set_defaults(handler=self._handle_list)

        # Comando 'actualizar'
        p_upgrade = subparsers.add_parser("actualizar", help="Actualizar el sistema y los paquetes de TPT.")
        p_upgrade.add_argument("--no-apply", action="store_true", help="Descarga las actualizaciones pero no las instala (para AADPO).")
        p_upgrade.set_defaults(handler=self._handle_upgrade)

        # Comando 'gui'
        p_gui = subparsers.add_parser("gui", help="Lanzar la Interfaz Gráfica de Usuario.")
        p_gui.set_defaults(handler=self._handle_gui)

        # Comando 'system-integrate'
        p_sys = subparsers.add_parser("system-integrate", help="Integra TPT con el sistema (ej. para AADPO).")
        p_sys_sub = p_sys.add_subparsers(title="Acciones de integración", dest="action", required=True)
        p_sys_install = p_sys_sub.add_parser("install", help="Instala el servicio AADPO de systemd.")
        p_sys_install.set_defaults(handler=self._handle_system_integrate_install)
        p_sys_uninstall = p_sys_sub.add_parser("uninstall", help="Desinstala el servicio AADPO de systemd.")
        p_sys_uninstall.set_defaults(handler=self._handle_system_integrate_uninstall)

        return parser

    def _handle_search(self, args):
        """Maneja la lógica de búsqueda y muestra los resultados en una tabla."""
        with Live(Spinner("dots", text=f"Buscando '{args.termino}'..."), console=self.console) as live:
            results = self.pm.search(args.termino)

        if not results:
            self.logger.warning(f"No se encontraron paquetes para '{args.termino}'.")
            return

        table = Table(title=f"Resultados para '[bold cyan]{args.termino}[/bold cyan]'")
        table.add_column("Nombre", style="magenta", no_wrap=True)
        table.add_column("Versión", style="green")
        table.add_column("Formato", style="yellow")
        table.add_column("Descripción", style="cyan")

        for pkg in results:
            table.add_row(pkg['name'], pkg.get('version', 'N/A'), pkg.get('format', 'N/A'), pkg.get('description', ''))

        self.console.print(table)

    def _handle_install(self, args):
        """Maneja la instalación de paquetes."""
        self.logger.info(f"Se intentará instalar: [bold magenta]{', '.join(args.nombres_paquete)}[/bold magenta]")
        if not Confirm.ask("¿Proceder con la instalación?", default=True, console=self.console):
            self.logger.warning("Instalación cancelada.")
            return

        for pkg_name in args.nombres_paquete:
            self.pm.install(pkg_name)

    def _handle_uninstall(self, args):
        """Maneja la desinstalación de paquetes."""
        self.logger.warning(f"Se intentará desinstalar: [bold red]{', '.join(args.nombres_paquete)}[/bold red]")
        if not Confirm.ask("¿Estás seguro de que quieres desinstalar estos paquetes?", default=False, console=self.console):
            self.logger.info("Desinstalación cancelada.")
            return

        for pkg_name in args.nombres_paquete:
            self.pm.uninstall(pkg_name)

    def _handle_list(self, args):
        """Muestra los paquetes instalados en una tabla."""
        installed_pkgs = self.pm.list_installed()

        if not installed_pkgs:
            self.logger.info("No hay paquetes instalados a través de TPT.")
            return

        table = Table(title="Paquetes Instalados por TPT")
        table.add_column("Nombre", style="magenta")
        table.add_column("Versión", style="green")
        table.add_column("Manejador", style="yellow")

        for name, data in installed_pkgs.items():
            handler = data.get("installation_details", {}).get("handler", "Desconocido")
            version = data.get("version", "N/A")
            table.add_row(name, version, handler)

        self.console.print(table)

    def _handle_upgrade(self, args):
        if args.no_apply:
            self.logger.info("Modo AADPO: Descargando actualizaciones sin aplicar...")
        else:
            self.logger.info("Iniciando proceso de actualización completo...")

        self.pm.upgrade(no_apply=args.no_apply)

    def _handle_gui(self, args):
        self.logger.info("Lanzando la Interfaz Gráfica de Usuario GTK4...")
        try:
            from ..gui.main_window import run_gui
            run_gui(self.pm)
        except ImportError as e:
            self.logger.critical(f"No se pudo lanzar la GUI: {e}")
            self.logger.warning("Asegúrate de que tienes las dependencias de GTK4 instaladas.")
            self.logger.warning("En Debian/Ubuntu: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1")
            self.logger.warning("O con pip: pip install PyGObject")
            sys.exit(1)

    def _handle_system_integrate_install(self, args):
        """Maneja la instalación del servicio de systemd."""
        self.logger.info("Instalando servicio AADPO de systemd...")
        if not Confirm.ask("Esto instalará un servicio en /etc/systemd/system. ¿Continuar?", console=self.console):
            self.logger.warning("Instalación del servicio cancelada.")
            return
        self.pm.system_integrate_install()

    def _handle_system_integrate_uninstall(self, args):
        """Maneja la desinstalación del servicio de systemd."""
        self.logger.info("Desinstalando servicio AADPO de systemd...")
        self.pm.system_integrate_uninstall()
