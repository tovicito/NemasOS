import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

import os
import subprocess
from pathlib import Path
from gi.repository import Gtk, Adw, Gio

# Esta vez, la ruta al proyecto se maneja en el lanzador,
# pero dejamos un fallback por si se ejecuta directamente.
try:
    from tpt_project.core.config import Configuracion
    from tpt_project.utils.i18n import _
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root))
    from tpt_project.core.config import Configuracion
    from tpt_project.utils.i18n import _


def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        return result
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error ejecutando {' '.join(command)}: {e}")
        return None

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'resources/setup_window.ui'))
class SetupWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'SetupWindow'

    carousel = Gtk.Template.Child()
    back_button = Gtk.Template.Child()
    next_button = Gtk.Template.Child()

    welcome_next_button = Gtk.Template.Child()
    language_combo = Gtk.Template.Child()
    repo_list_view = Gtk.Template.Child()
    repo_entry = Gtk.Template.Child()
    repo_add_button = Gtk.Template.Child()
    repo_remove_button = Gtk.Template.Child()
    repo_restore_button = Gtk.Template.Child()
    rich_switch = Gtk.Template.Child()
    confirm_switch = Gtk.Template.Child()
    timeout_spin = Gtk.Template.Child()
    ssl_switch = Gtk.Template.Child()
    aadpo_switch = Gtk.Template.Child()
    finish_button = Gtk.Template.Child()

    lang_map = { 0: "en", 1: "es", 2: "pt" }
    lang_map_rev = { "en": 0, "es": 1, "pt": 2 }

    def __init__(self, app, **kwargs):
        super().__init__(application=app, **kwargs)
        self.app = app
        self.config = Configuracion()
        self.settings = self.config.load_settings()

        self.setup_repos_list()
        self.load_initial_state()
        self.connect_signals()

    def load_initial_state(self):
        try:
            with open(self.config.DIR_CONFIG / "lang.conf", "r") as f:
                self.language_combo.set_selected(self.lang_map_rev.get(f.read().strip(), 0))
        except (IOError, FileNotFoundError):
            self.language_combo.set_selected(0)

        self.rich_switch.set_active(self.settings.get("use_rich", True))
        self.confirm_switch.set_active(self.settings.get("confirm_actions", True))
        self.aadpo_switch.set_active(self.settings.get("aadpo_enabled", False))
        self.timeout_spin.set_value(self.settings.get("network_timeout", 15))
        self.ssl_switch.set_active(self.settings.get("ssl_verify", True))

        self.update_nav_buttons()

    def connect_signals(self):
        self.welcome_next_button.connect("clicked", lambda x: self.carousel.scroll_to(self.carousel.get_nth_page(1), True))
        self.back_button.connect("clicked", lambda x: self.carousel.scroll_to(self.carousel.get_previous_page(), True))
        self.next_button.connect("clicked", lambda x: self.carousel.scroll_to(self.carousel.get_next_page(), True))
        self.finish_button.connect("clicked", self._on_finish)
        self.carousel.connect("page-changed", lambda c, i: self.update_nav_buttons())

        self.repo_add_button.connect("clicked", self._on_repo_add)
        self.repo_remove_button.connect("clicked", self._on_repo_remove)
        self.repo_restore_button.connect("clicked", self._on_repo_restore)

    def setup_repos_list(self):
        self.repo_model = Gtk.StringList()
        try:
            with open(self.config.ARCHIVO_REPOS, 'r') as f:
                repos = [line.strip() for line in f if line.strip()]
            for repo in repos: self.repo_model.append(repo)
        except (IOError, FileNotFoundError):
            for repo in self.config.REPOS_POR_DEFECTO: self.repo_model.append(repo)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda fac, item: item.set_child(Gtk.Label(halign=Gtk.Align.START)))
        factory.connect("bind", lambda fac, item: item.get_child().set_label(item.get_item().get_string()))

        self.repo_list_view.set_model(Gtk.SingleSelection(model=self.repo_model))
        self.repo_list_view.set_factory(factory)

    def update_nav_buttons(self):
        current_page = self.carousel.get_position()
        self.back_button.set_visible(current_page > 0)
        self.next_button.set_visible(current_page < self.carousel.get_n_pages() - 1)

    def _on_repo_add(self, button):
        repo_url = self.repo_entry.get_text()
        if repo_url and repo_url.startswith("https://"):
            self.repo_model.append(repo_url)
            self.repo_entry.set_text("")

    def _on_repo_remove(self, button):
        selection_model = self.repo_list_view.get_model()
        selected_pos = selection_model.get_selected()
        if selected_pos != Gtk.INVALID_LIST_POSITION:
            self.repo_model.remove(selected_pos)

    def _on_repo_restore(self, button):
        self.repo_model.remove_all()
        for repo in self.config.REPOS_POR_DEFECTO:
            self.repo_model.append(repo)

    def _on_finish(self, button):
        print("Aplicando configuración...")
        self.config.asegurar_directorios()

        lang_code = self.lang_map.get(self.language_combo.get_selected(), "en")
        with open(self.config.DIR_CONFIG / "lang.conf", "w") as f: f.write(lang_code)

        locale_dir = Path(__file__).resolve().parent.parent / "locale"
        po_file = locale_dir / lang_code / "LC_MESSAGES" / "tpt.po"
        mo_file = locale_dir / lang_code / "LC_MESSAGES" / "tpt.mo"
        if po_file.exists():
            if run_command(["msgfmt", str(po_file), "-o", str(mo_file)]):
                print(f"Idioma '{lang_code}' compilado con éxito.")

        repos = [self.repo_model.get_string(i) for i in range(self.repo_model.get_n_items())]
        with open(self.config.ARCHIVO_REPOS, "w") as f: f.write("\n".join(repos))

        self.settings["use_rich"] = self.rich_switch.get_active()
        self.settings["confirm_actions"] = self.confirm_switch.get_active()
        self.settings["aadpo_enabled"] = self.aadpo_switch.get_active()
        self.settings["network_timeout"] = self.timeout_spin.get_value_as_int()
        self.settings["ssl_verify"] = self.ssl_switch.get_active()
        self.config.save_settings(self.settings)

        print("¡Configuración guardada!")
        self.app.quit()

class TPTSetupApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id="io.github.tovicito.tpt.setup", **kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = SetupWindow(app)
        win.present()

def run_setup_gui():
    app = TPTSetupApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    run_setup_gui()
