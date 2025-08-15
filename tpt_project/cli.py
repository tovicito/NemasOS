import argparse
import sys
import logging
from .core.package_manager import PackageManager
from .utils.exceptions import TPTError, MultipleSourcesFoundError
from .utils.i18n import _

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.traceback import Traceback
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

class CLI:
    """Maneja toda la interacción con el usuario a través de la línea de comandos."""

    def __init__(self, pm: PackageManager, logger: logging.Logger):
        self.pm = pm
        self.logger = logger
        self.settings = self.pm.config.load_settings()

        # Inicializar (o no) rich basado en la configuración
        if self.settings.get("use_rich", True) and HAS_RICH:
            self.console = Console()
        else:
            self.console = None

    def _confirm(self, question: str, default=False) -> bool:
        """Wrapper para Confirm.ask que respeta la configuración."""
        if not self.settings.get("confirm_actions", True):
            return True # Si las confirmaciones están desactivadas, siempre proceder
        if not self.console:
            # Fallback para cuando rich no está disponible
            response = input(f"{question} [y/N]: ").lower().strip()
            return response == "y"
        return Confirm.ask(question, default=default, console=self.console)

    def run(self, argv=None):
        """Punto de entrada principal para la CLI."""
        parser = self._create_parser()
        # Añadir el argumento --lang al parser principal también para que aparezca en la ayuda
        parser.add_argument('--lang', help=_('Forzar un idioma (ej. es, en)'))
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
            self.logger.warning(_("\nOperación cancelada por el usuario."))
            sys.exit(130)
        except Exception as e:
            self.logger.critical(_("Ocurrió un error inesperado: {}").format(e), exc_info=True)
            if self.console:
                self.console.print_exception(show_locals=True)
            sys.exit(1)

    def _create_parser(self):
        """Configura argparse para todos los comandos."""
        parser = argparse.ArgumentParser(
            prog="tpt",
            description=_("TPT - La Herramienta de Paquetes Total. Un gestor de paquetes universal."),
            epilog=_("Para más ayuda sobre un comando específico, usa: tpt <comando> --help")
        )
        parser.add_argument("-v", "--version", action="version", version="%(prog)s 5.0.0")
        subparsers = parser.add_subparsers(title=_("Comandos disponibles"), dest="command")

        # Comando 'buscar'
        p_search = subparsers.add_parser("buscar", help=_("Buscar un paquete en los repositorios."))
        p_search.add_argument("termino", help=_("Término de búsqueda."))
        p_search.set_defaults(handler=self._handle_search)

        # Comando 'instalar'
        p_install = subparsers.add_parser("instalar", help=_("Instalar uno o más paquetes."))
        p_install.add_argument("nombres_paquete", nargs='+', help=_("Nombre(s) del(los) paquete(s) a instalar."))
        p_install.set_defaults(handler=self._handle_install)

        # Comando 'desinstalar'
        p_uninstall = subparsers.add_parser("desinstalar", help=_("Desinstalar uno o más paquetes."))
        p_uninstall.add_argument("nombres_paquete", nargs='+', help=_("Nombre(s) del(los) paquete(s) a desinstalar."))
        p_uninstall.set_defaults(handler=self._handle_uninstall)

        # Comando 'listar'
        p_list = subparsers.add_parser("listar", help=_("Listar todos los paquetes instalados por TPT."))
        p_list.set_defaults(handler=self._handle_list)

        # Comando 'actualizar'
        p_upgrade = subparsers.add_parser("actualizar", help=_("Actualizar el sistema y los paquetes de TPT."))
        p_upgrade.add_argument("--no-apply", action="store_true", help=_("Descarga las actualizaciones pero no las instala (para AADPO)."))
        p_upgrade.set_defaults(handler=self._handle_upgrade)

        # Comando 'gui'
        p_gui = subparsers.add_parser("gui", help=_("Lanzar la Interfaz Gráfica de Usuario."))
        p_gui.set_defaults(handler=self._handle_gui)

        # Comando 'system-integrate'
        p_sys = subparsers.add_parser("system-integrate", help=_("Integra TPT con el sistema (ej. para AADPO)."))
        p_sys_sub = p_sys.add_subparsers(title=_("Acciones de integración"), dest="action", required=True)
        p_sys_install = p_sys_sub.add_parser("install", help=_("Instala el servicio AADPO de systemd."))
        p_sys_install.set_defaults(handler=self._handle_system_integrate_install)
        p_sys_uninstall = p_sys_sub.add_parser("uninstall", help=_("Desinstala el servicio AADPO de systemd."))
        p_sys_uninstall.set_defaults(handler=self._handle_system_integrate_uninstall)

        # Comando 'aadpo-status'
        p_status = subparsers.add_parser("aadpo-status", help=_("Muestra las actualizaciones pendientes de AADPO."))
        p_status.set_defaults(handler=self._handle_aadpo_status)

        return parser

    def _handle_search(self, args):
        """Maneja la lógica de búsqueda y muestra los resultados."""
        if self.console:
            with Live(Spinner("dots", text=_("Buscando '{}'...").format(args.termino)), console=self.console) as live:
                results = self.pm.search(args.termino)
        else:
            self.logger.info(_("Buscando '{}'...").format(args.termino))
            results = self.pm.search(args.termino)

        if not results:
            self.logger.warning(_("No se encontraron paquetes para '{}'.").format(args.termino))
            return

        if self.console:
            table = Table(title=_("Resultados para '[bold cyan]{}[/bold cyan]'").format(args.termino))
            table.add_column(_("Fuente"), style="blue", no_wrap=True)
            table.add_column(_("Nombre"), style="magenta", no_wrap=True)
            table.add_column(_("Versión"), style="green")
            table.add_column(_("Descripción"), style="cyan")
            for pkg in results:
                table.add_row(pkg.get('source', 'tpt'), pkg.get('name', 'N/A'), pkg.get('version', 'N/A'), pkg.get('description', ''))
            self.console.print(table)
        else:
            # Salida en texto plano
            print(_("--- Resultados de la Búsqueda ---"))
            for pkg in results:
                print(f"  {pkg.get('name', 'N/A')} ({pkg.get('version', 'N/A')})")
                print(f"    {_('Fuente')}: {pkg.get('source', 'tpt')}")
                print(f"    {_('Descripción')}: {pkg.get('description', '')}\n")

    def _handle_install(self, args):
        """Maneja la instalación de paquetes, incluyendo la desambiguación de fuentes."""
        for pkg_name in args.nombres_paquete:
            self.logger.info(_("Procesando instalación para: [bold magenta]{}[/bold magenta]").format(pkg_name))

            def do_install(pkg_name, source=None):
                try:
                    self.pm.install(pkg_name, source=source)
                except MultipleSourcesFoundError as e:
                    self.logger.warning(e.message)
                    available_sources = sorted(list(set(choice['source'] for choice in e.choices)))
                    source_choice = Prompt.ask(
                        _("Por favor, elige una fuente de instalación"),
                        choices=available_sources,
                        default=available_sources[0]
                    )
                    self.logger.info(_("Intentando instalar '{}' desde la fuente seleccionada: [bold blue]{}[/bold blue]").format(pkg_name, source_choice))
                    do_install(pkg_name, source=source_choice)
                except TPTError as e:
                    self.logger.error(_("No se pudo instalar '{}': {}").format(pkg_name, e.message))
                except Exception as e:
                    self.logger.critical(_("Ocurrió un error inesperado al procesar '{}': {}").format(pkg_name, e), exc_info=True)

            if self._confirm(_("¿Deseas proceder con la instalación de '{}'?").format(pkg_name), default=True):
                do_install(pkg_name)
            else:
                self.logger.info(_("Instalación de '{}' cancelada por el usuario.").format(pkg_name))

    def _handle_uninstall(self, args):
        """Maneja la desinstalación de paquetes."""
        self.logger.warning(_("Se intentará desinstalar: [bold red]{}[/bold red]").format(', '.join(args.nombres_paquete)))
        if not self._confirm(_("¿Estás seguro de que quieres desinstalar estos paquetes?"), default=False):
            self.logger.info(_("Desinstalación cancelada."))
            return

        for pkg_name in args.nombres_paquete:
            self.pm.uninstall(pkg_name)

    def _handle_list(self, args):
        """Muestra los paquetes instalados."""
        installed_pkgs = self.pm.list_installed()

        if not installed_pkgs:
            self.logger.info(_("No hay paquetes instalados a través de TPT."))
            return

        if self.console:
            table = Table(title=_("Paquetes Instalados por TPT"))
            table.add_column(_("Nombre"), style="magenta")
            table.add_column(_("Versión"), style="green")
            table.add_column(_("Manejador"), style="yellow")
            for name, data in installed_pkgs.items():
                handler = data.get("installation_details", {}).get("handler", _("Desconocido"))
                version = data.get("version", "N/A")
                table.add_row(name, version, handler)
            self.console.print(table)
        else:
            print(_("--- Paquetes Instalados por TPT ---"))
            for name, data in installed_pkgs.items():
                version = data.get("version", "N/A")
                print(f"  - {name} (v{version})")

    def _handle_upgrade(self, args):
        if args.no_apply:
            self.logger.info(_("Modo AADPO: Descargando actualizaciones sin aplicar..."))
            self.pm.upgrade(no_apply=True)
        else:
            self.logger.info(_("Iniciando proceso de actualización completo..."))
            if self._confirm(_("Esto buscará y aplicará actualizaciones del sistema y de los paquetes TPT. ¿Continuar?"), default=True):
                self.pm.upgrade(no_apply=False)
            else:
                self.logger.info(_("Proceso de actualización cancelado."))

    def _handle_gui(self, args):
        self.logger.info(_("Lanzando la Interfaz Gráfica de Usuario GTK4..."))
        self.logger.info(_("Por favor, ejecuta 'tpt-gui' directamente."))
        # Ya no intentamos lanzar la GUI desde aquí para evitar problemas de importación.
        # Se asume que hay un ejecutable 'tpt-gui' en el PATH.

    def _handle_system_integrate_install(self, args):
        """Maneja la instalación del servicio de systemd."""
        self.logger.info(_("Instalando servicio AADPO de systemd..."))
        if not self._confirm(_("Esto instalará un servicio en /etc/systemd/system. ¿Continuar?")):
            self.logger.warning(_("Instalación del servicio cancelada."))
            return
        self.pm.system_integrate_install()

    def _handle_system_integrate_uninstall(self, args):
        """Maneja la desinstalación del servicio de systemd."""
        self.logger.info(_("Desinstalando servicio AADPO de systemd..."))
        self.pm.system_integrate_uninstall()

    def _handle_aadpo_status(self, args):
        """Muestra el estado de las actualizaciones pendientes de AADPO."""
        self.logger.info(_("Comprobando el estado de AADPO..."))
        actions = self.pm.get_aadpo_status()

        if actions is None:
            self.logger.success(_("No hay actualizaciones pendientes de AADPO."))
            return

        if not actions:
            self.logger.error(_("Se encontró un manifiesto de AADPO, pero está vacío o corrupto."))
            return

        if self.console:
            table = Table(title=_("Actualizaciones Pendientes de AADPO"))
            table.add_column(_("Tipo de Acción"), style="cyan")
            table.add_column(_("Detalles"), style="magenta")
            for action in actions:
                action_type = action.get("action", _("Desconocida"))
                details_str = ""
                if action_type == "install_tpt":
                    details_str = _("Paquete: {}, Archivo: {}").format(action.get('name'), action.get('file', 'N/A'))
                elif action_type == "sys_update":
                    details_str = _("Gestor: {}").format(action.get('manager'))
                else:
                    details_str = str(action)
                table.add_row(action_type, details_str)
            self.console.print(table)
        else:
            print(_("--- Actualizaciones Pendientes de AADPO ---"))
            for action in actions:
                print(f"  - {_('Acción')}: {action.get('action')}, {_('Detalles')}: {action}")
