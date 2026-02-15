import os

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, GObject
from package_manager import PackageManager

PKGDATADIR = os.environ.get('PKGDATADIR', '/app/share/tte.nemas.Epola')


def _template_kwargs(ui_filename):
    resource_path = f'/tte/nemas/Epola/{ui_filename}'
    try:
        Gio.resources_get_info(resource_path, Gio.ResourceLookupFlags.NONE)
        return {'resource_path': resource_path}
    except GLib.Error:
        return {'filename': os.path.join(PKGDATADIR, ui_filename)}


@Gtk.Template(**_template_kwargs('app_widget.ui'))
class EpolaAppWidget(Gtk.Box):
    __gtype_name__ = 'EpolaAppWidget'
    __gsignals__ = {
        'install-requested': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }

    app_icon = Gtk.Template.Child()
    app_name = Gtk.Template.Child()
    app_summary = Gtk.Template.Child()
    install_button = Gtk.Template.Child()

    def __init__(self, app_info, **kwargs):
        super().__init__(**kwargs)
        self.app_info = app_info
        self.app_name.set_label(app_info.name)
        self.app_summary.set_label(app_info.summary)
        self.app_icon.set_from_icon_name(app_info.icon)

        if app_info.installed:
            self.install_button.set_label("Instalada")
            self.install_button.set_sensitive(False)
            self.install_button.get_style_context().remove_class("suggested-action")
        else:
            self.install_button.connect("clicked", self.on_install_clicked)

    def on_install_clicked(self, button):
        button.set_sensitive(False)
        button.set_label("Instalando...")
        self.emit("install-requested", self.app_info)


@Gtk.Template(**_template_kwargs('window.ui'))
class EpolaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'EpolaWindow'

    toast_overlay = Gtk.Template.Child()
    explore_grid = Gtk.Template.Child()
    installed_grid = Gtk.Template.Child()
    updates_grid = Gtk.Template.Child()
    updates_empty_page = Gtk.Template.Child()
    explore_empty_page = Gtk.Template.Child()
    installed_empty_page = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    auto_updates_switch = Gtk.Template.Child()
    ppa_switch = Gtk.Template.Child()
    flatpak_switch = Gtk.Template.Child()
    snap_switch = Gtk.Template.Child()
    packagekit_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from const import APP_ID

        self.settings = Gio.Settings.new(APP_ID)
        self.settings.bind("auto-updates", self.auto_updates_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-ppa", self.ppa_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-flatpak", self.flatpak_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-snap", self.snap_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-packagekit", self.packagekit_switch, "active", Gio.SettingsBindFlags.DEFAULT)

        self.pm = PackageManager()
        self.pm.connect('apps-loaded', self.on_apps_loaded)
        self.pm.connect('installed-loaded', self.on_installed_loaded)
        self.pm.connect('updates-loaded', self.on_updates_loaded)
        self.pm.connect('operation-completed', self.on_operation_completed)

        self.main_stack.connect("notify::visible-child-name", self.on_tab_changed)
        self.pm.load_apps()

    def _show_toast(self, message):
        self.toast_overlay.add_toast(Adw.Toast.new(message))

    def on_tab_changed(self, stack, pspec):
        name = stack.get_visible_child_name()
        if name == "explore":
            self.pm.load_apps(self.search_entry.get_text().strip())
        elif name == "installed":
            self.pm.load_installed_apps()
        elif name == "updates":
            self.pm.check_updates()

    def on_apps_loaded(self, pm, apps):
        self._fill_grid(self.explore_grid, apps)
        self.explore_empty_page.set_visible(len(apps) == 0)

    def on_installed_loaded(self, pm, apps):
        self._fill_grid(self.installed_grid, apps)
        self.installed_empty_page.set_visible(len(apps) == 0)

    def on_updates_loaded(self, pm, apps):
        self._fill_grid(self.updates_grid, apps)
        self.updates_empty_page.set_visible(len(apps) == 0)
        self.updates_grid.set_visible(len(apps) > 0)

    def on_operation_completed(self, pm, success, message):
        if success:
            self._show_toast('Operación completada correctamente')
            self.pm.load_installed_apps()
            self.pm.check_updates()
        else:
            self._show_toast(message or 'La operación falló')

    def _fill_grid(self, grid, apps):
        child = grid.get_first_child()
        while child:
            grid.remove(child)
            child = grid.get_first_child()

        for app in apps:
            widget = EpolaAppWidget(app)
            widget.connect("install-requested", self.on_install_requested)
            grid.append(widget)

    def on_install_requested(self, widget, app_info):
        self.pm.install_app(app_info.id, app_info.backend)

    @Gtk.Template.Callback()
    def on_search_changed(self, entry):
        text = entry.get_text().strip()
        self.pm.load_apps(text)

    @Gtk.Template.Callback()
    def on_refresh_updates_clicked(self, button):
        self.pm.check_updates()
        self._show_toast('Buscando actualizaciones...')

    @Gtk.Template.Callback()
    def on_reset_data_clicked(self, button):
        self.settings.reset('auto-updates')
        self.settings.reset('use-ppa')
        self.settings.reset('use-flatpak')
        self.settings.reset('use-snap')
        self.settings.reset('use-packagekit')
        self.settings.reset('theme')
        self.settings.set_boolean('first-run', True)

        app = self.get_application()
        self.close()
        from setup import EpolaSetupWindow
        setup = EpolaSetupWindow(application=app)
        setup.present()
