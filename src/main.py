import sys
import os
import signal
import gettext
from gi.repository import Gtk, Gio, Adw, Gdk

# Handle package name and path
APP_ID = 'tte.nemas.Epola'

# Logic for finding data dir
PKGDATADIR = os.environ.get('PKGDATADIR')
if not PKGDATADIR:
    # Try common locations
    for path in ['/app/share/tte.nemas.Epola', '/usr/local/share/tte.nemas.Epola', '/usr/share/tte.nemas.Epola']:
        if os.path.exists(path):
            PKGDATADIR = path
            break
if not PKGDATADIR:
    # Fallback to local development path
    PKGDATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))

# Initialize gettext
gettext.bindtextdomain(APP_ID, os.path.join(PKGDATADIR, 'locale'))
gettext.textdomain(APP_ID)
_ = gettext.gettext

# Local imports
from window import EpolaWindow
from setup import EpolaSetupWindow

class EpolaApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.settings = None

    def do_activate(self):
        window = self.get_active_window()
        if not window:
            try:
                self.settings = Gio.Settings.new(APP_ID)
                first_run = self.settings.get_boolean('first-run')
            except:
                first_run = True

            if first_run:
                setup = EpolaSetupWindow(application=self)
                setup.present()
                setup.connect('destroy', lambda w: self.show_main_window())
            else:
                self.show_main_window()

    def show_main_window(self):
        window = EpolaWindow(application=self)
        window.present()

    def do_startup(self):
        Adw.Application.do_startup(self)

        # Load resources
        resource_file = os.path.join(PKGDATADIR, 'tte.nemas.Epola.gresource')
        if os.path.exists(resource_file):
            resource = Gio.Resource.load(resource_file)
            resource._register()

        # Load CSS
        provider = Gtk.CssProvider()
        try:
            provider.load_from_resource('/tte/nemas/Epola/style.css')
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Could not load CSS: {e}")

def main():
    app = EpolaApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    # Add src to path for direct execution
    sys.path.insert(0, os.path.dirname(__file__))
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(main())
