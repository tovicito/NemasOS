import sys
import os
import signal
import gettext
from gi.repository import Gtk, Gio, Adw, Gdk

# Handle package name and path
APP_ID = 'tte.nemas.Epola'
PKGDATADIR = os.environ.get('PKGDATADIR', os.path.join(os.path.dirname(__file__), '..', 'data'))

# Initialize gettext
gettext.bindtextdomain(APP_ID, os.path.join(PKGDATADIR, 'locale'))
gettext.textdomain(APP_ID)
_ = gettext.gettext

from .window import EpolaWindow
from .setup import EpolaSetupWindow

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

        # Load resources
        resource_file = os.path.join(PKGDATADIR, 'tte.nemas.Epola.gresource')
        if not os.path.exists(resource_file):
             # Fallback for development structure
             resource_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tte.nemas.Epola.gresource')

        if os.path.exists(resource_file):
            resource = Gio.Resource.load(resource_file)
            resource._register()

def main():
    app = EpolaApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    # Add parent dir to path so we can do 'from . import ...' if run as script
    # but it's better to run as a module.
    # For now, this helper allows running directly.
    if __package__ is None:
        path = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, path)
        import src
        __package__ = "src"

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(main())
