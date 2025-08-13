import os
from pathlib import Path

class Configuracion:
    """Gestiona toda la configuración, rutas y constantes para TPT."""
    def __init__(self):
        self.ARCHIVO_MANIFIESTO_REPO = "packages.json"
        self.RAMA_POR_DEFECTO = "regular"
        self.DIR_EJECUTABLES_ROOT = Path("/usr/local/bin")
        self.DIR_APLICACIONES_ROOT = Path("/usr/share/applications")
        self.DIR_OPT_ROOT = Path("/opt")

        if os.geteuid() == 0:
            self.DIR_ESTADO = Path("/var/lib/tpt")
            self.DIR_CACHE = Path("/var/cache/tpt")
            self.DIR_LOGS = Path("/var/log/tpt")
            self.DIR_CONFIG = Path("/etc/tpt")
        else:
            self.DIR_ESTADO = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "tpt"
            self.DIR_CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "tpt"
            self.DIR_LOGS = self.DIR_ESTADO
            self.DIR_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "tpt"

        self.BD_PAQUETES_INSTALADOS = self.DIR_ESTADO / "installed.json"
        self.DIR_CACHE_REPOS = self.DIR_CACHE / "repos"
        self.DIR_STAGING = self.DIR_ESTADO / "staging" # Para AADPO
        self.ICON_CACHE_DIR = self.DIR_CACHE / "icons"
        self.ARCHIVO_LOG = self.DIR_LOGS / "tpt.log"

        # Lista de parches aplicados
        self.LISTA_PARCHES_APLICADOS = self.DIR_ESTADO / "tpt-patches-applied.list"

        if Path("tpt-repos.list").exists():
            self.ARCHIVO_REPOS = Path("tpt-repos.list")
        else:
            self.ARCHIVO_REPOS = self.DIR_CONFIG / "tpt-repos.list"
        self.ARCHIVO_RAMA = self.DIR_CONFIG / "branch.txt"

        self.REPOS_POR_DEFECTO = [
            "https://raw.githubusercontent.com/tovicito/NemasOS/regular/",
            "https://raw.githubusercontent.com/tovicito/Nemas-community/main/"
        ]

    def asegurar_directorios(self):
        """Crea todos los directorios necesarios si no existen."""
        # La GUI puede llamar a esto desde un hilo diferente
        try:
            dirs_to_create = [
                self.DIR_ESTADO, self.DIR_CACHE, self.DIR_LOGS, self.DIR_CONFIG,
                self.DIR_CACHE_REPOS, self.ICON_CACHE_DIR, self.DIR_STAGING
            ]
            for d in dirs_to_create:
                d.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Este error es lo suficientemente serio como para detener las cosas.
            print(f"Error Crítico: No se pudo crear el directorio {d}: {e}. Asegúrate de tener permisos.", file=sys.stderr)
            sys.exit(1)
