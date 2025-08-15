import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

import os
import threading
import logging
import json
from pathlib import Path
from gi.repository import Gtk, Adw, Gio, GLib

from ..core.package_manager import PackageManager
from .gtk_logger import GtkLogHandler

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'resources/tpt_window.ui'))
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    search_entry = Gtk.Template.Child()
    log_view = Gtk.Template.Child()
    results_list_view = Gtk.Template.Child()
    results_model = Gtk.Template.Child()
    details_view = Gtk.Template.Child()
    install_button = Gtk.Template.Child()

    def __init__(self, app, **kwargs):
        super().__init__(application=app, **kwargs)
        self.app = app
        self.search_thread = None
        self.action_thread = None
        self.search_results_data = {}

        # Configurar el logger de la GUI
        self.log_buffer = self.log_view.get_buffer()
        self.log_buffer.create_mark("end_mark", self.log_buffer.get_end_iter(), False)
        gui_log_handler = GtkLogHandler(self.log_buffer)
        logging.getLogger("tpt").addHandler(gui_log_handler)
        logging.getLogger("tpt").info("GUI iniciada y logger conectado.")

        # Conectar señales
        self.results_list_view.get_selection_model().connect("selection-changed", self._on_selection_changed)

    @Gtk.Template.Callback()
    def _on_list_item_setup(self, factory, list_item):
        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        name_label = Gtk.Label()
        name_label.set_halign(Gtk.Align.START)
        name_label.set_use_markup(True)
        desc_label = Gtk.Label()
        desc_label.set_halign(Gtk.Align.START)
        desc_label.set_wrap(True)
        desc_label.get_style_context().add_class("caption")
        box.append(name_label)
        box.append(desc_label)
        list_item.set_child(box)

    @Gtk.Template.Callback()
    def _on_list_item_bind(self, factory, list_item):
        box = list_item.get_child()
        name_label = box.get_first_child()
        desc_label = box.get_last_child()
        pkg_name = list_item.get_item().get_string()
        pkg_details = self.search_results_data.get(pkg_name)
        if pkg_details:
            version = pkg_details.get('version', 'N/A')
            format_type = pkg_details.get('format') or Path(pkg_details.get('download_url', '')).suffix
            description = pkg_details.get('description', 'Sin descripción.')
            name_markup = f"<b>{GLib.markup_escape_text(pkg_name)}</b> <small>({GLib.markup_escape_text(version)})</small>"
            desc_text = f"<i>Formato: {GLib.markup_escape_text(str(format_type))}</i>\n{GLib.markup_escape_text(description)}"
            name_label.set_markup(name_markup)
            desc_label.set_markup(desc_text)

    def _on_selection_changed(self, selection_model, position, n_items):
        """Actualiza el panel de detalles cuando cambia la selección."""
        selected_pos = selection_model.get_selection().first()
        if selected_pos is None:
            self.install_button.set_sensitive(False)
            self.details_view.get_buffer().set_text("")
            return

        selected_pkg_name = self.results_model.get_string(selected_pos)
        pkg_details = self.search_results_data.get(selected_pkg_name)

        if pkg_details:
            details_text = json.dumps(pkg_details, indent=2, ensure_ascii=False)
            self.details_view.get_buffer().set_text(details_text)
            self.install_button.set_sensitive(True)
        else:
            self.install_button.set_sensitive(False)
            self.details_view.get_buffer().set_text("")

    @Gtk.Template.Callback()
    def _on_search_changed(self, entry):
        if self.search_thread and self.search_thread.is_alive():
            pass
        search_text = entry.get_text()
        if len(search_text) < 3:
            self.results_model.splice(0, self.results_model.get_n_items(), [])
            return
        self.search_thread = threading.Thread(target=self._search_worker, args=(search_text,))
        self.search_thread.daemon = True
        self.search_thread.start()

    def _search_worker(self, search_text):
        try:
            results = self.app.pm.search(search_text)
            GLib.idle_add(self._update_search_results, results)
        except Exception as e:
            logging.getLogger("tpt").error(f"Error en el hilo de búsqueda: {e}", exc_info=True)

    def _update_search_results(self, results):
        self.results_model.splice(0, self.results_model.get_n_items(), [])
        self.search_results_data.clear()
        pkg_names = [pkg['name'] for pkg in results]
        for pkg in results:
            self.search_results_data[pkg['name']] = pkg
        self.results_model.splice(0, 0, pkg_names)
        logging.getLogger("tpt").info(f"Búsqueda completada. Se encontraron {len(results)} paquetes.")
        return False

    @Gtk.Template.Callback()
    def _on_install_clicked(self, button):
        """Inicia la instalación del paquete seleccionado en un hilo secundario."""
        selection_model = self.results_list_view.get_selection_model()
        selected_pos = selection_model.get_selection().first()
        if selected_pos is None:
            return

        pkg_name = self.results_model.get_string(selected_pos)

        if self.action_thread and self.action_thread.is_alive():
            logging.getLogger("tpt").warning("Ya hay una acción en progreso.")
            return

        self.action_thread = threading.Thread(target=self._install_worker, args=(pkg_name,))
        self.action_thread.daemon = True
        self.action_thread.start()

    def _install_worker(self, pkg_name):
        """Trabajo de instalación que se ejecuta en un hilo separado."""
        try:
            self.app.pm.install(pkg_name)
        except Exception as e:
            logging.getLogger("tpt").error(f"Falló la instalación de '{pkg_name}': {e}", exc_info=True)

class TPTGtkApp(Adw.Application):
    def __init__(self, pm: PackageManager, **kwargs):
        super().__init__(application_id="io.github.tovicito.tpt", **kwargs)
        self.pm = pm
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = MainWindow(app)
        win.present()

def run_gui(pm: PackageManager):
    app = TPTGtkApp(pm)
    return app.run(sys.argv)
