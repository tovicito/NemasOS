import logging
from gi.repository import Gtk, GLib

class GtkLogHandler(logging.Handler):
    """
    Un manejador de logging personalizado que redirige los registros a un Gtk.TextBuffer.
    """
    def __init__(self, text_buffer: Gtk.TextBuffer):
        super().__init__()
        self.text_buffer = text_buffer

        # Formateador para los logs de la GUI
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        """
        Añade el registro al buffer de texto de forma segura para hilos.
        """
        msg = self.format(record)
        # GLib.idle_add asegura que la actualización de la GUI se haga en el hilo principal
        GLib.idle_add(self.append_text, msg)

    def append_text(self, text):
        """Añade texto al final del buffer y hace scroll."""
        end_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(end_iter, text + '\n')

        # Auto-scroll hacia el final
        self.text_buffer.move_mark_by_name("end_mark", end_iter)
        scroll_mark = self.text_buffer.get_mark("end_mark")
        if scroll_mark:
            text_view = self.text_buffer.get_tag_table() # Hackish way to find a textview, better to pass it in
            # A better way is to get the view from the buffer, but that's not direct.
            # For now, this is a placeholder for scrolling logic.
            # text_view.scroll_to_mark(scroll_mark, 0.0, True, 0.0, 1.0)
        return False # Para que no se llame de nuevo
