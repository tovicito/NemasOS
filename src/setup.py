import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
from const import APP_ID

@Gtk.Template(resource_path='/tte/nemas/Epola/setup.ui')
class EpolaSetupWindow(Adw.Window):
    __gtype_name__ = 'EpolaSetupWindow'

    setup_stack = Gtk.Template.Child()
    auto_updates_switch = Gtk.Template.Child()
    ppa_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new(APP_ID)
        self.settings.bind("auto-updates", self.auto_updates_switch, "active", Gio.SettingsBindFlags.DEFAULT)

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
        self.close()
