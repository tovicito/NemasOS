import os

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
from const import APP_ID

PKGDATADIR = os.environ.get('PKGDATADIR', '/app/share/tte.nemas.Epola')


def _template_kwargs(ui_filename):
    resource_path = f'/tte/nemas/Epola/{ui_filename}'
    try:
        Gio.resources_get_info(resource_path, Gio.ResourceLookupFlags.NONE)
        return {'resource_path': resource_path}
    except GLib.Error:
        return {'filename': os.path.join(PKGDATADIR, ui_filename)}


@Gtk.Template(**_template_kwargs('setup.ui'))
class EpolaSetupWindow(Adw.Window):
    __gtype_name__ = 'EpolaSetupWindow'
    __gsignals__ = {
        'setup-completed': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    setup_stack = Gtk.Template.Child()
    setup_auto_updates_switch = Gtk.Template.Child()
    setup_ppa_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new(APP_ID)
        self.settings.bind("auto-updates", self.auto_updates_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-ppa", self.ppa_switch, "active", Gio.SettingsBindFlags.DEFAULT)

    @Gtk.Template.Callback()
    def on_next_clicked(self, button):
        current = self.setup_stack.get_visible_child_name()
        if current == 'welcome':
            self.setup_stack.set_visible_child_name('theme')
        elif current == 'theme':
            self.setup_stack.set_visible_child_name('features')

    @Gtk.Template.Callback()
    def on_theme_light_clicked(self, button):
        self.settings.set_string('theme', 'light')
        self.apply_theme('light')

    @Gtk.Template.Callback()
    def on_theme_dark_clicked(self, button):
        self.settings.set_string('theme', 'dark')
        self.apply_theme('dark')

    def apply_theme(self, theme):
        style_manager = Adw.StyleManager.get_default()
        if theme == 'light':
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
        elif theme == 'dark':
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    @Gtk.Template.Callback()
    def on_finish_clicked(self, button):
        self.settings.set_boolean('first-run', False)
        self.emit('setup-completed')
        self.close()
