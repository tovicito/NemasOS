import argparse
import sys
import logging
import json
import shutil
from pathlib import Path
from .core.package_manager import PackageManager
from .utils.exceptions import TPTError, MultipleSourcesFoundError
from .utils import system

class CLI:
    """
    Maneja la interacción de la línea de comandos para TPT.
    Diseñada para ser usada tanto por humanos como por scripts.
    """

    def __init__(self, pm: PackageManager, logger: logging.Logger):
        self.pm = pm
        self.logger = logger

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
        except Exception as e:
            self.logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
            sys.exit(1)

    def _create_parser(self):
        """Configura argparse para todos los comandos."""
        parser = argparse.ArgumentParser(
            prog="tpt",
            description="TPT - La Herramienta de Paquetes Total (Backend CLI)."
        )
        parser.add_argument("-v", "--version", action="version", version="%(prog)s 6.0.0-plasma")
        subparsers = parser.add_subparsers(title="Comandos disponibles", dest="command")

        p_search = subparsers.add_parser("search", help="Busca un paquete.")
        p_search.add_argument("term", help="Término de búsqueda.")
        p_search.add_argument("--json", action="store_true", help="Devolver resultados en formato JSON.")
        p_search.set_defaults(handler=self._handle_search)

        p_details = subparsers.add_parser("details", help="Obtiene detalles de un paquete.")
        p_details.add_argument("package_name", help="Nombre del paquete.")
        p_details.set_defaults(handler=self._handle_details)

        p_install = subparsers.add_parser("install", help="Instala un paquete.")
        p_install.add_argument("package_name", help="Nombre del paquete.")
        p_install.add_argument("--source", help="Fuente específica desde la que instalar.")
        p_install.set_defaults(handler=self._handle_install)

        p_uninstall = subparsers.add_parser("uninstall", help="Desinstala un paquete.")
        p_uninstall.add_argument("package_name", help="Nombre del paquete.")
        p_uninstall.set_defaults(handler=self._handle_uninstall)

        p_upgrade = subparsers.add_parser("upgrade", help="Busca y aplica actualizaciones.")
        p_upgrade.add_argument("--no-apply", action="store_true", help="Prepara las actualizaciones pero no las aplica.")
        p_upgrade.set_defaults(handler=self._handle_upgrade)

        p_sys = subparsers.add_parser("system-integrate", help="Integra TPT con el sistema.")
        p_sys.add_argument("action", choices=["install", "uninstall"], help="Acción a realizar.")
        p_sys.set_defaults(handler=self._handle_system_integrate)

        return parser

    def _handle_search(self, args):
        results = self.pm.search(args.term)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            if not results:
                self.logger.info(f"No se encontraron paquetes para '{args.term}'.")
                return
            for pkg in results:
                print(f"- {pkg.get('name')} ({pkg.get('version', 'N/A')}) [{pkg.get('source', 'tpt')}]")
                print(f"  {pkg.get('description', '')}")

    def _handle_details(self, args):
        results = self.pm.search(args.package_name)
        exact_match = next((p for p in results if p['name'] == args.package_name), None)
        if exact_match:
            print(json.dumps(exact_match, indent=2))
        else:
            self.logger.error(f"No se encontraron detalles para el paquete '{args.package_name}'.")
            sys.exit(1)

    def _handle_install(self, args):
        self.logger.info(f"Iniciando instalación de '{args.package_name}'...")
        try:
            self.pm.install(args.package_name, source=args.source)
            self.logger.info(f"Instalación de '{args.package_name}' completada con éxito.")
        except MultipleSourcesFoundError as e:
            self.logger.error(f"Error: El paquete '{e.package_name}' existe en múltiples fuentes: {[c['source'] for c in e.choices]}.")
            self.logger.error("Por favor, especifica una fuente con --source <fuente>.")
            sys.exit(1)
        except TPTError as e:
            self.logger.error(f"Error durante la instalación: {e.message}")
            sys.exit(1)

    def _handle_uninstall(self, args):
        self.logger.info(f"Iniciando desinstalación de '{args.package_name}'...")
        try:
            self.pm.uninstall(args.package_name)
            self.logger.info(f"Desinstalación de '{args.package_name}' completada con éxito.")
        except TPTError as e:
            self.logger.error(f"Error durante la desinstalación: {e.message}")
            sys.exit(1)

    def _handle_upgrade(self, args):
        self.logger.info("Buscando actualizaciones...")
        self.pm.upgrade(no_apply=args.no_apply)

    def _handle_system_integrate(self, args):
        # Asumimos que el script se ejecuta desde la raíz del proyecto descomprimido
        backend_source_dir = Path.cwd() / "backend"

        # Rutas de destino estándar en sistemas Debian/KDE
        backend_exec_dest = Path("/usr/lib/x86_64-linux-gnu/libexec/discover-backend-tpt")
        backend_meta_dest = Path("/usr/share/discover/backends/plasma-discover-backend-tpt.json")
        dbus_service_dest = Path("/usr/share/dbus-1/services/io.github.tovicito.tpt.service")

        if args.action == "install":
            self.logger.info("Instalando integración de TPT con Plasma Discover...")
            try:
                # Crear directorios de destino si no existen
                system.execute_command(["mkdir", "-p", str(backend_exec_dest.parent)], self.logger, as_root=True)
                system.execute_command(["mkdir", "-p", str(backend_meta_dest.parent)], self.logger, as_root=True)
                system.execute_command(["mkdir", "-p", str(dbus_service_dest.parent)], self.logger, as_root=True)

                # Copiar archivos
                system.execute_command(["cp", str(backend_source_dir / "plasma-discover-backend-tpt"), str(backend_exec_dest)], self.logger, as_root=True)
                system.execute_command(["cp", str(backend_source_dir / "plasma-discover-backend-tpt.json"), str(backend_meta_dest)], self.logger, as_root=True)
                system.execute_command(["cp", str(backend_source_dir / "io.github.tovicito.tpt.service"), str(dbus_service_dest)], self.logger, as_root=True)

                # Dar permisos de ejecución al backend
                system.execute_command(["chmod", "+x", str(backend_exec_dest)], self.logger, as_root=True)

                self.logger.info("Integración completada. Reinicia Plasma Discover para ver los cambios.")
            except TPTError as e:
                self.logger.error(f"Falló la instalación de la integración: {e}")
                sys.exit(1)

        elif args.action == "uninstall":
            self.logger.info("Desinstalando integración de TPT con Plasma Discover...")
            try:
                system.execute_command(["rm", "-f", str(backend_exec_dest)], self.logger, as_root=True)
                system.execute_command(["rm", "-f", str(backend_meta_dest)], self.logger, as_root=True)
                system.execute_command(["rm", "-f", str(dbus_service_dest)], self.logger, as_root=True)
                self.logger.info("Desinstalación de la integración completada.")
            except TPTError as e:
                self.logger.error(f"Falló la desinstalación de la integración: {e}")
                sys.exit(1)
