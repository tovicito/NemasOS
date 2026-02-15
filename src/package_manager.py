import logging
import shutil
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
                    if term:
                        res = self._run(['flatpak', 'search', term, '--columns=application,name,description,version,icon'])
                        if res and res.returncode == 0:
                            for line in res.stdout.splitlines():
                                parts = [p.strip() for p in line.split('\t')]
                                if len(parts) >= 2:
                                    apps.append(AppInfo(parts[0], parts[1], parts[2] if len(parts) > 2 else '', parts[4] if len(parts) > 4 and parts[4] else 'application-x-executable', 'Flatpak', version=parts[3] if len(parts) > 3 else ''))
                    else:
                        apps.extend(self._flatpak_featured())
                except Exception:
                    LOG.exception('Failed to load Flatpak apps')

            if self.settings.get_boolean('use-snap') and term:
                try:
                    res = self._run(['snap', 'find', term])
                    if res and res.returncode == 0:
                        lines = [l for l in res.stdout.splitlines() if l.strip()]
                        for line in lines[1:]:
                            parts = line.split()
                            if parts:
                                name = parts[0]
                                summary = ' '.join(parts[3:]) if len(parts) > 3 else ''
                                apps.append(AppInfo(name, name, summary, 'io.snapcraft.SnapStore', 'Snap'))
                except Exception:
                    LOG.exception('Failed to load Snap apps')

            if self.settings.get_boolean('use-packagekit') and term:
                try:
                    res = self._run(['pkcon', 'search', 'name', term])
                    if res and res.returncode == 0:
                        for line in res.stdout.splitlines():
                            if line.startswith(' '):
                                continue
                            if ';' in line and ('installed' in line.lower() or 'available' in line.lower()):
                                pkg_id = line.split()[-1]
                                name = pkg_id.split(';')[0]
                                apps.append(AppInfo(pkg_id, name, 'Paquete del sistema', 'system-software-install', 'PackageKit'))
                except Exception:
                    LOG.exception('Failed to load PackageKit apps')

            dedup = {}
            for app in apps:
                dedup[(app.backend, app.id)] = app
            GLib.idle_add(self.emit, 'apps-loaded', list(dedup.values())[:100])

        threading.Thread(target=_load, daemon=True).start()

    def load_installed_apps(self):
        def _load():
            apps = []

            if self.settings.get_boolean('use-flatpak'):
                try:
                    res = self._run(['flatpak', 'list', '--app', '--columns=application,name,description,version,icon'])
                    if res and res.returncode == 0:
                        for line in res.stdout.splitlines():
                            parts = [p.strip() for p in line.split('\t')]
                            if len(parts) >= 2:
                                apps.append(AppInfo(parts[0], parts[1], parts[2] if len(parts) > 2 else '', parts[4] if len(parts) > 4 and parts[4] else 'application-x-executable', 'Flatpak', True, parts[3] if len(parts) > 3 else ''))
                except Exception:
                    LOG.exception('Failed flatpak installed listing')

            if self.settings.get_boolean('use-snap'):
                try:
                    res = self._run(['snap', 'list'])
                    if res and res.returncode == 0:
                        for line in res.stdout.splitlines()[1:]:
                            parts = line.split()
                            if parts:
                                apps.append(AppInfo(parts[0], parts[0], 'Snap instalado', 'io.snapcraft.SnapStore', 'Snap', True, parts[1] if len(parts) > 1 else ''))
                except Exception:
                    LOG.exception('Failed snap installed listing')

            GLib.idle_add(self.emit, 'installed-loaded', apps)

        threading.Thread(target=_load, daemon=True).start()

    def check_updates(self):
        def _load():
            updates = []

            if self.settings.get_boolean('use-flatpak'):
                try:
                    res = self._run(['flatpak', 'remote-ls', '--updates', '--app', '--columns=application,name,version'])
                    if res and res.returncode == 0:
                        for line in res.stdout.splitlines():
                            parts = [p.strip() for p in line.split('\t')]
                            if len(parts) >= 2:
                                updates.append(AppInfo(parts[0], parts[1], 'Actualización disponible', 'software-update-available', 'Flatpak', True, parts[2] if len(parts) > 2 else ''))
                except Exception:
                    LOG.exception('Failed flatpak update check')

            if self.settings.get_boolean('use-snap'):
                try:
                    res = self._run(['snap', 'refresh', '--list'])
                    if res and res.returncode == 0:
                        for line in res.stdout.splitlines()[1:]:
                            parts = line.split()
                            if parts:
                                updates.append(AppInfo(parts[0], parts[0], 'Actualización Snap disponible', 'software-update-available', 'Snap', True, parts[1] if len(parts) > 1 else ''))
                except Exception:
                    LOG.exception('Failed snap update check')

            GLib.idle_add(self.emit, 'updates-loaded', updates)

        threading.Thread(target=_load, daemon=True).start()

    def install_app(self, app_id, backend):
        def _install():
            success = False
            error_message = ''
            try:
                if backend == 'Flatpak':
                    res = self._run(['flatpak', 'install', '--user', '-y', app_id])
                    if res and res.returncode != 0:
                        res = self._run(['pkexec', 'flatpak', 'install', '-y', app_id])
                    success = bool(res and res.returncode == 0)
                    error_message = '' if success else (res.stderr.strip() if res else 'No se encontró flatpak')
                elif backend == 'Snap':
                    res = self._run(['pkexec', 'snap', 'install', app_id])
                    success = bool(res and res.returncode == 0)
                    error_message = '' if success else (res.stderr.strip() if res else 'No se encontró snap')
                elif backend == 'PackageKit':
                    res = self._run(['pkexec', 'pkcon', 'install', '-y', app_id])
                    success = bool(res and res.returncode == 0)
                    error_message = '' if success else (res.stderr.strip() if res else 'No se encontró pkcon')
                else:
                    error_message = f'Backend no soportado: {backend}'
            except Exception as exc:
                LOG.exception('Install failed for %s via %s', app_id, backend)
                error_message = str(exc)

            GLib.idle_add(self.emit, 'operation-completed', success, error_message)

        threading.Thread(target=_install, daemon=True).start()
