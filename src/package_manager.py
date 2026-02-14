import subprocess
import threading
from gi.repository import GLib, Gio, GObject

class AppInfo:
    def __init__(self, id, name, summary, icon, backend, installed=False, version=""):
        self.id = id
        self.name = name
        self.summary = summary
        self.icon = icon
        self.backend = backend
        self.installed = installed
        self.version = version

class PackageManager(GObject.Object):
    __gsignals__ = {
        'apps-loaded': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'installed-loaded': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'updates-loaded': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'operation-completed': (GObject.SignalFlags.RUN_FIRST, None, (bool, str)),
    }

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings.new('tte.nemas.Epola')

    def load_apps(self, search_term=None):
        def _load():
            apps = []

            # Flatpak
            if self.settings.get_boolean('use-flatpak'):
                try:
                    if search_term:
                        cmd = ['flatpak', 'search', '--columns=application,name,description,version,icon', search_term]
                    else:
                        cmd = ['flatpak', 'remote-ls', '--columns=application,name,description,version,icon', '--app']

                    res = subprocess.run(cmd, capture_output=True, text=True)
                    if res.returncode == 0:
                        for line in res.stdout.strip().split('\n'):
                            parts = line.split('\t')
                            if len(parts) >= 3:
                                apps.append(AppInfo(parts[0].strip(), parts[1].strip(), parts[2].strip(),
                                                   parts[4].strip() if len(parts)>4 else "application-x-executable",
                                                   "Flatpak", version=parts[3].strip() if len(parts)>3 else ""))
                except: pass

            # Snap
            if self.settings.get_boolean('use-snap'):
                try:
                    if search_term:
                        cmd = ['snap', 'find', search_term]
                        res = subprocess.run(cmd, capture_output=True, text=True)
                        if res.returncode == 0:
                            lines = res.stdout.strip().split('\n')
                            if len(lines) > 1:
                                for line in lines[1:]:
                                    parts = line.split()
                                    if len(parts) >= 1:
                                        apps.append(AppInfo(parts[0], parts[0], " ".join(parts[3:]) if len(parts)>3 else "", "snap", "Snap"))
                except: pass

            # PackageKit (pkcon)
            if self.settings.get_boolean('use-packagekit'):
                try:
                    if search_term:
                        cmd = ['pkcon', 'search', 'name', search_term]
                        res = subprocess.run(cmd, capture_output=True, text=True)
                        if res.returncode == 0:
                            current_pkg = {}
                            for line in res.stdout.split('\n'):
                                if line.startswith('Available') or line.startswith('Installed'):
                                    if 'id' in current_pkg:
                                        apps.append(AppInfo(current_pkg['id'], current_pkg['name'],
                                                            current_pkg.get('summary', ''), 'system-software-install',
                                                            'PackageKit', current_pkg['installed']))
                                    current_pkg = {'installed': line.startswith('Installed')}
                                elif ':' in line:
                                    k, v = line.split(':', 1)
                                    k, v = k.strip().lower(), v.strip()
                                    if k == 'package':
                                        current_pkg['id'] = v
                                        current_pkg['name'] = v.split(';')[0]
                                    elif k == 'summary':
                                        current_pkg['summary'] = v
                            if 'id' in current_pkg:
                                apps.append(AppInfo(current_pkg['id'], current_pkg['name'],
                                                    current_pkg.get('summary', ''), 'system-software-install',
                                                    'PackageKit', current_pkg['installed']))
                except: pass

            GLib.idle_add(self.emit, 'apps-loaded', apps)
        threading.Thread(target=_load, daemon=True).start()

    def load_installed_apps(self):
        def _load():
            apps = []
            # Flatpak
            try:
                res = subprocess.run(['flatpak', 'list', '--columns=application,name,description,version,icon', '--app'], capture_output=True, text=True)
                if res.returncode == 0:
                    for line in res.stdout.strip().split('\n'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            apps.append(AppInfo(parts[0], parts[1], parts[2] if len(parts)>2 else "", parts[4] if len(parts)>4 else "application-x-executable", "Flatpak", True))
            except: pass
            GLib.idle_add(self.emit, 'installed-loaded', apps)
        threading.Thread(target=_load, daemon=True).start()

    def check_updates(self):
        def _load():
            updates = []
            try:
                res = subprocess.run(['flatpak', 'remote-ls', '--updates', '--columns=application,name,version'], capture_output=True, text=True)
                if res.returncode == 0:
                    for line in res.stdout.strip().split('\n'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            updates.append(AppInfo(parts[0], parts[1], "Actualización disponible", "software-update-available", "Flatpak", True, version=parts[2] if len(parts)>2 else ""))
            except: pass
            GLib.idle_add(self.emit, 'updates-loaded', updates)
        threading.Thread(target=_load, daemon=True).start()

    def install_app(self, app_id, backend):
        def _install():
            success = False
            try:
                if backend == "Flatpak":
                    # Try user install first to avoid auth prompt if possible
                    res = subprocess.run(['flatpak', 'install', '--user', '-y', app_id], capture_output=True)
                    if res.returncode != 0:
                        res = subprocess.run(['flatpak', 'install', '-y', app_id], capture_output=True)
                    success = res.returncode == 0
                elif backend == "Snap":
                    # Use pkexec for snap since it needs root
                    res = subprocess.run(['pkexec', 'snap', 'install', app_id], capture_output=True)
                    success = res.returncode == 0
                elif backend == "PackageKit":
                    res = subprocess.run(['pkcon', 'install', '-y', app_id], capture_output=True)
                    success = res.returncode == 0
            except: pass
            GLib.idle_add(self.emit, 'operation-completed', success, "")
        threading.Thread(target=_install, daemon=True).start()
