import logging
import subprocess
import threading
from gi.repository import GLib, Gio, GObject


LOG = logging.getLogger(__name__)


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

    def _run(self, cmd):
        if not cmd:
            return None
        if shutil.which(cmd[0]) is None:
            LOG.info('Command not available: %s', cmd[0])
            return None
        return subprocess.run(cmd, capture_output=True, text=True)

    def _flatpak_featured(self):
        apps = []
        remotes = self._run(['flatpak', 'remotes', '--columns=name'])
        if not remotes or remotes.returncode != 0:
            return apps

        remote_list = [r.strip() for r in remotes.stdout.splitlines() if r.strip()]
        for remote in remote_list:
            listing = self._run(['flatpak', 'remote-ls', remote, '--app', '--columns=application,name,description,version,icon'])
            if not listing or listing.returncode != 0:
                continue
            for line in listing.stdout.splitlines()[:60]:
                parts = [p.strip() for p in line.split('\t')]
                if len(parts) >= 2:
                    apps.append(AppInfo(
                        parts[0],
                        parts[1] or parts[0],
                        parts[2] if len(parts) > 2 else '',
                        parts[4] if len(parts) > 4 and parts[4] else 'application-x-executable',
                        'Flatpak',
                        False,
                        parts[3] if len(parts) > 3 else ''
                    ))
            if apps:
                break
        return apps

    def load_apps(self, search_term=None):
        def _load():
            apps = []
            term = (search_term or '').strip()

            if self.settings.get_boolean('use-flatpak'):
                try:
                    cmd = ['flatpak', 'search', '--columns=application,name,description,version,icon', search_term] if search_term else ['flatpak', 'remote-ls', '--columns=application,name,description,version,icon', '--app']
                    res = subprocess.run(cmd, capture_output=True, text=True)
                    if res.returncode == 0:
                        for line in res.stdout.strip().split('\n'):
                            parts = line.split('\t')
                            if len(parts) >= 3:
                                apps.append(AppInfo(parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[4].strip() if len(parts) > 4 else 'application-x-executable', 'Flatpak', version=parts[3].strip() if len(parts) > 3 else ''))
                    else:
                        LOG.warning('flatpak command failed: %s', res.stderr.strip())
                except Exception as exc:
                    LOG.exception('Failed to load Flatpak apps: %s', exc)

            if self.settings.get_boolean('use-snap'):
                try:
                    if search_term:
                        res = subprocess.run(['snap', 'find', search_term], capture_output=True, text=True)
                        if res.returncode == 0:
                            lines = res.stdout.strip().split('\n')
                            if len(lines) > 1:
                                for line in lines[1:]:
                                    parts = line.split()
                                    if len(parts) >= 1:
                                        apps.append(AppInfo(parts[0], parts[0], ' '.join(parts[3:]) if len(parts) > 3 else '', 'snap', 'Snap'))
                        else:
                            LOG.warning('snap find failed: %s', res.stderr.strip())
                except Exception as exc:
                    LOG.exception('Failed to load Snap apps: %s', exc)

            if self.settings.get_boolean('use-packagekit'):
                try:
                    if search_term:
                        res = subprocess.run(['pkcon', 'search', 'name', search_term], capture_output=True, text=True)
                        if res.returncode == 0:
                            current_pkg = {}
                            for line in res.stdout.split('\n'):
                                if line.startswith('Available') or line.startswith('Installed'):
                                    if 'id' in current_pkg:
                                        apps.append(AppInfo(current_pkg['id'], current_pkg['name'], current_pkg.get('summary', ''), 'system-software-install', 'PackageKit', current_pkg['installed']))
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
                                apps.append(AppInfo(current_pkg['id'], current_pkg['name'], current_pkg.get('summary', ''), 'system-software-install', 'PackageKit', current_pkg['installed']))
                        else:
                            LOG.warning('pkcon search failed: %s', res.stderr.strip())
                except Exception as exc:
                    LOG.exception('Failed to load PackageKit apps: %s', exc)

            GLib.idle_add(self.emit, 'apps-loaded', apps)

        threading.Thread(target=_load, daemon=True).start()

    def load_installed_apps(self):
        def _load():
            apps = []
            try:
                res = subprocess.run(['flatpak', 'list', '--columns=application,name,description,version,icon', '--app'], capture_output=True, text=True)
                if res.returncode == 0:
                    for line in res.stdout.strip().split('\n'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            apps.append(AppInfo(parts[0], parts[1], parts[2] if len(parts) > 2 else '', parts[4] if len(parts) > 4 else 'application-x-executable', 'Flatpak', True))
                else:
                    LOG.warning('flatpak list failed: %s', res.stderr.strip())
            except Exception as exc:
                LOG.exception('Failed to load installed apps: %s', exc)

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
                            updates.append(AppInfo(parts[0], parts[1], 'Actualización disponible', 'software-update-available', 'Flatpak', True, version=parts[2] if len(parts) > 2 else ''))
                else:
                    LOG.warning('flatpak remote-ls --updates failed: %s', res.stderr.strip())
            except Exception as exc:
                LOG.exception('Failed to check updates: %s', exc)

            GLib.idle_add(self.emit, 'updates-loaded', updates)

        threading.Thread(target=_load, daemon=True).start()

    def install_app(self, app_id, backend):
        def _install():
            success = False
            error_message = ''

            try:
                if backend == 'Flatpak':
                    res = subprocess.run(['flatpak', 'install', '--user', '-y', app_id], capture_output=True, text=True)
                    if res.returncode != 0:
                        res = subprocess.run(['flatpak', 'install', '-y', app_id], capture_output=True, text=True)
                    success = res.returncode == 0
                    error_message = res.stderr.strip() if not success else ''
                elif backend == 'Snap':
                    res = subprocess.run(['pkexec', 'snap', 'install', app_id], capture_output=True, text=True)
                    success = res.returncode == 0
                    error_message = res.stderr.strip() if not success else ''
                elif backend == 'PackageKit':
                    res = subprocess.run(['pkcon', 'install', '-y', app_id], capture_output=True, text=True)
                    success = res.returncode == 0
                    error_message = res.stderr.strip() if not success else ''
                else:
                    error_message = f'Backend no soportado: {backend}'
            except Exception as exc:
                error_message = str(exc)
                LOG.exception('Failed to install app %s with backend %s: %s', app_id, backend, exc)

            GLib.idle_add(self.emit, 'operation-completed', success, error_message)

        threading.Thread(target=_install, daemon=True).start()
