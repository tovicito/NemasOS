from gi.repository import Gtk, Adw, GLib, Gio, GObject
from .package_manager import PackageManager

@Gtk.Template(resource_path='/tte/nemas/Epola/app_widget.ui')
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
            self.install_button.set_label("Abrir")
            self.install_button.get_style_context().remove_class("suggested-action")
        else:
            self.install_button.connect("clicked", self.on_install_clicked)

    def on_install_clicked(self, button):
        button.set_sensitive(False)
        button.set_label("Instalando...")
        self.emit("install-requested", self.app_info)

@Gtk.Template(resource_path='/tte/nemas/Epola/window.ui')
class EpolaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'EpolaWindow'

    explore_grid = Gtk.Template.Child()
    installed_grid = Gtk.Template.Child()
    updates_grid = Gtk.Template.Child()
    updates_empty_page = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    auto_updates_switch = Gtk.Template.Child()
    flatpak_switch = Gtk.Template.Child()
    snap_switch = Gtk.Template.Child()
    packagekit_switch = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from .const import APP_ID
        self.settings = Gio.Settings.new(APP_ID)
        self.settings.bind("auto-updates", self.auto_updates_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-flatpak", self.flatpak_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-snap", self.snap_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("use-packagekit", self.packagekit_switch, "active", Gio.SettingsBindFlags.DEFAULT)

        self.pm = PackageManager()
        self.pm.connect('apps-loaded', self.on_apps_loaded)
        self.pm.connect('installed-loaded', self.on_installed_loaded)
        self.pm.connect('updates-loaded', self.on_updates_loaded)

        self.main_stack.connect("notify::visible-child-name", self.on_tab_changed)
        self.pm.load_apps()

    def on_tab_changed(self, stack, pspec):
        name = stack.get_visible_child_name()
        if name == "explore":
            self.pm.load_apps()
        elif name == "installed":
            self.pm.load_installed_apps()
        elif name == "updates":
            self.pm.check_updates()

    def on_apps_loaded(self, pm, apps):
        self._fill_grid(self.explore_grid, apps)

    def on_installed_loaded(self, pm, apps):
        self._fill_grid(self.installed_grid, apps)

    def on_updates_loaded(self, pm, apps):
        self._fill_grid(self.updates_grid, apps)
        self.updates_empty_page.set_visible(len(apps) == 0)
        self.updates_grid.set_visible(len(apps) > 0)

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
        text = entry.get_text()
        if len(text) >= 3:
            self.pm.load_apps(text)
        elif len(text) == 0:
            self.pm.load_apps()
