import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

import os
import threading
import logging
from pathlib import Path
from gi.repository import Gtk, Adw, Gio, GLib

from ..core.package_manager import PackageManager
from ..utils.exceptions import MultipleSourcesFoundError
from .gtk_logger import GtkLogHandler
from ..utils.i18n import _

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'resources/tpt_window.ui'))
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    search_entry = Gtk.Template.Child()
    log_view = Gtk.Template.Child()
    results_list_view = Gtk.Template.Child()
    results_model = Gtk.Template.Child()
    install_button = Gtk.Template.Child()
    main_spinner = Gtk.Template.Child()
    details_grid = Gtk.Template.Child()
    details_description = Gtk.Template.Child()
    details_title = Gtk.Template.Child()

    def __init__(self, app, **kwargs):
        super().__init__(application=app, **kwargs)
        self.app = app
        self.action_thread = None
        self.search_results_data = {}

        self.log_buffer = self.log_view.get_buffer()
        self.log_buffer.create_mark("end_mark", self.log_buffer.get_end_iter(), False)
        gui_log_handler = GtkLogHandler(self.log_buffer)
        logging.getLogger("tpt").addHandler(gui_log_handler)
        logging.getLogger("tpt").info(_("GUI iniciada y logger conectado."))

        self.results_list_view.get_selection_model().connect("selection-changed", self._on_selection_changed)
        self.search_entry.set_placeholder_text(_("Buscar paquetes..."))
        self.install_button.set_label(_("Instalar"))

    def _set_busy(self, busy):
        self.main_spinner.set_spinning(busy)
        self.main_spinner.set_visible(busy)
        self.search_entry.set_sensitive(not busy)
        self.install_button.set_sensitive(not busy and self._is_package_selected())

    def _is_package_selected(self):
        return self.results_list_view.get_selection_model().get_selection().first() is not None

    @Gtk.Template.Callback()
    def _on_list_item_setup(self, factory, list_item):
        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        name_label = Gtk.Label(halign=Gtk.Align.START, use_markup=True)
        source_label = Gtk.Label(halign=Gtk.Align.START, use_markup=True)
        source_label.get_style_context().add_class("caption")
        box.append(name_label)
        box.append(source_label)
        list_item.set_child(box)

    @Gtk.Template.Callback()
    def _on_list_item_bind(self, factory, list_item):
        box = list_item.get_child()
        name_label, source_label = box.get_first_child(), box.get_last_child()
        pkg_name = list_item.get_item().get_string()
        pkg_details = self.search_results_data.get(pkg_name)
        if pkg_details:
            version = pkg_details.get('version', 'N/A')
            source = pkg_details.get('source', 'tpt')
            name_markup = f"<b>{GLib.markup_escape_text(pkg_name)}</b> <small>({GLib.markup_escape_text(version)})</small>"
            source_markup = f"<small>{_('Fuente')}: {GLib.markup_escape_text(source)}</small>"
            name_label.set_markup(name_markup)
            source_label.set_markup(source_markup)

    def _on_selection_changed(self, selection_model, position, n_items):
        while self.details_grid.get_row_at(0): self.details_grid.remove_row(0)

        selected_pos = selection_model.get_selection().first()
        if selected_pos is None:
            self.install_button.set_sensitive(False)
            self.details_grid.set_visible(False)
            self.details_description.set_visible(False)
            self.details_title.set_label(_("Detalles del Paquete"))
            return

        selected_pkg_name = self.results_model.get_string(selected_pos)
        pkg_details = self.search_results_data.get(selected_pkg_name)

        if pkg_details:
            self.details_title.set_label(selected_pkg_name)
            details_map = {
                _("Versión:"): pkg_details.get('version', 'N/A'),
                _("Fuente:"): pkg_details.get('source', 'tpt'),
                _("Formato:"): pkg_details.get('format', 'N/A'),
                _("Repositorio:"): pkg_details.get('repository_url', 'N/A'),
            }
            for i, (key, value) in enumerate(details_map.items()):
                label = Gtk.Label(label=key, halign=Gtk.Align.START, selectable=True)
                label.get_style_context().add_class("dim-label")
                val = Gtk.Label(label=str(value), halign=Gtk.Align.START, wrap=True, selectable=True)
                self.details_grid.attach(label, 0, i, 1, 1)
                self.details_grid.attach(val, 1, i, 1, 1)

            self.details_description.set_text(pkg_details.get('description', _('Sin descripción.')))
            self.details_grid.set_visible(True)
            self.details_description.set_visible(True)
            self.install_button.set_sensitive(not self.main_spinner.is_spinning())
        else:
            self.install_button.set_sensitive(False)
            self.details_grid.set_visible(False)
            self.details_description.set_visible(False)
            self.details_title.set_label(_("Detalles del Paquete"))

    @Gtk.Template.Callback()
    def _on_search_changed(self, entry):
        search_text = entry.get_text()
        if len(search_text) < 3:
            self.results_model.splice(0, self.results_model.get_n_items(), [])
            return
        if self.action_thread and self.action_thread.is_alive(): return
        self._set_busy(True)
        self.action_thread = threading.Thread(target=self._search_worker, args=(search_text,))
        self.action_thread.daemon = True
        self.action_thread.start()

    def _search_worker(self, search_text):
        try:
            results = self.app.pm.search(search_text)
            GLib.idle_add(self._update_search_results, results)
        except Exception as e:
            logging.getLogger("tpt").error(_("Error en el hilo de búsqueda: {}").format(e), exc_info=True)
            GLib.idle_add(self._set_busy, False)

    def _update_search_results(self, results):
        self.results_model.splice(0, self.results_model.get_n_items(), [])
        self.search_results_data.clear()
        pkg_names = [pkg['name'] for pkg in results]
        for pkg in results: self.search_results_data[pkg['name']] = pkg
        self.results_model.splice(0, 0, pkg_names)
        logging.getLogger("tpt").info(_("Búsqueda completada. Se encontraron {} paquetes.").format(len(results)))
        self._set_busy(False)
        return False

    @Gtk.Template.Callback()
    def _on_install_clicked(self, button):
        if not self._is_package_selected(): return
        pkg_name = self.results_model.get_string(self.results_list_view.get_selection_model().get_selection().first())
        if self.action_thread and self.action_thread.is_alive():
            logging.getLogger("tpt").warning(_("Ya hay una acción en progreso."))
            return
        self._set_busy(True)
        self.action_thread = threading.Thread(target=self._install_worker, args=(pkg_name,))
        self.action_thread.daemon = True
        self.action_thread.start()

    def _install_worker(self, pkg_name, source=None):
        try:
            self.app.pm.install(pkg_name, source=source)
        except MultipleSourcesFoundError as e:
            GLib.idle_add(self._show_source_disambiguation_dialog, e)
            return
        except Exception as e:
            logging.getLogger("tpt").error(_("Falló la instalación de '{}': {}").format(pkg_name, e), exc_info=True)
        GLib.idle_add(self._set_busy, False)

    def _show_source_disambiguation_dialog(self, error):
        self._set_busy(False)
        dialog = Adw.MessageDialog.new(self, _("Múltiples Fuentes Encontradas"),
            _("El paquete '{}' está disponible en varias fuentes. Por favor, elige una para continuar.").format(error.package_name))
        sources = sorted(list(set(c['source'] for c in error.choices)))
        for source in sources:
            dialog.add_response(source, source.capitalize())
        dialog.set_default_response(sources[0])
        dialog.set_close_response("cancel")
        dialog.connect("response", self._on_source_dialog_response, error.package_name)
        dialog.present()

    def _on_source_dialog_response(self, dialog, response_id, pkg_name):
        if response_id != "cancel":
            logging.getLogger("tpt").info(_("Reintentando instalación de '{}' desde la fuente '{}'...").format(pkg_name, response_id))
            self._set_busy(True)
            self.action_thread = threading.Thread(target=self._install_worker, args=(pkg_name, response_id))
            self.action_thread.daemon = True
            self.action_thread.start()

class TPTGtkApp(Adw.Application):
    def __init__(self, pm: PackageManager, **kwargs):
        super().__init__(application_id="io.github.tovicito.tpt", **kwargs)
        self.pm = pm
        pm.progress_callback = self.on_pm_progress
        self.connect('activate', self.on_activate)
        self.win = None

    def on_activate(self, app):
        self.win = MainWindow(app)
        self.win.present()

    def on_pm_progress(self, current, total, message):
        logging.getLogger("tpt").info(f"[PROGRESO] {message}: {current}/{total}")

def run_gui(pm: PackageManager):
    app = TPTGtkApp(pm)
    return app.run(sys.argv)
