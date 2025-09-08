import os
import json
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, pyqtSlot, QThread, QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from ..style import *

# Try to import gpsd, but don't fail if it's not there (for testing on systems without it)
try:
    import gpsd
    GPSD_AVAILABLE = True
except ImportError:
    GPSD_AVAILABLE = False
    print("Advertencia: Módulo gpsd no encontrado. La funcionalidad de GPS estará deshabilitada.")

class GpsWorker(QObject):
    new_coordinates = pyqtSignal(float, float)
    def __init__(self):
        super().__init__()
        self.running = True
    @pyqtSlot()
    def run(self):
        if not GPSD_AVAILABLE: return
        try:
            gpsd.connect()
        except Exception as e:
            print(f"Error al conectar con gpsd: {e}. El hilo de GPS no se iniciará.")
            return
        while self.running:
            try:
                packet = gpsd.get_current()
                if packet.mode >= 2:
                    self.new_coordinates.emit(packet.lat, packet.lon)
            except Exception as e:
                print(f"Error en el bucle de GPS: {e}")
                time.sleep(5)
            time.sleep(2)

class WebEnginePage(QWebEnginePage):
    """Custom WebEnginePage to handle JavaScript console messages."""
    leaflet_loaded_signal = pyqtSignal()

    def javaScriptConsoleMessage(self, level, message, line, source_id):
        """Re-implementation to capture console messages."""
        # print(f"JS Console ({source_id}:{line}): {message}") # For debugging
        if message == "LEAFLET_LOADED":
            print("Handshake received from JavaScript: Leaflet is ready.")
            self.leaflet_loaded_signal.emit()

class MapPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setFont(QFont(KIA_FONT_FAMILY))
        self.map_loaded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        search_bar_widget = QWidget()
        search_bar_widget.setStyleSheet(f"background-color: {KIA_DARK_GREY};")
        search_bar_layout = QVBoxLayout(search_bar_widget)
        search_bar_layout.setContentsMargins(15, 10, 15, 10)

        search_row_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar dirección...")
        self.search_input.setStyleSheet(f"QLineEdit {{ border: 1px solid {KIA_HOVER_GREY}; border-radius: 8px; padding: 10px; background-color: {KIA_BLACK}; color: {KIA_LIGHT_GREY}; font-size: 16px; }}")
        self.search_button = QPushButton("Buscar")
        self.search_button.setStyleSheet(f"QPushButton {{ background-color: {KIA_VIOLET}; color: {KIA_BLACK}; border: none; border-radius: 8px; padding: 10px; font-weight: bold; font-size: 16px; }} QPushButton:hover {{ background-color: {KIA_VIOLET_LIGHT}; }}")
        search_row_layout.addWidget(self.search_input)
        search_row_layout.addWidget(self.search_button)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ff5555;")
        self.status_label.hide()

        search_bar_layout.addLayout(search_row_layout)
        search_bar_layout.addWidget(self.status_label)
        layout.addWidget(search_bar_widget)

        self.web_view = QWebEngineView()
        self.custom_page = WebEnginePage(self)
        self.web_view.setPage(self.custom_page)
        layout.addWidget(self.web_view)

        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_search_finished)

        self.search_button.clicked.connect(self.search_location)
        self.search_input.returnPressed.connect(self.search_location)
        self.custom_page.leaflet_loaded_signal.connect(self.on_leaflet_loaded)

        html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'map.html'))
        self.web_view.setUrl(QUrl.fromLocalFile(html_file_path))

    def on_leaflet_loaded(self):
        self.map_loaded = True
        self.setup_gps_thread()

    def setup_gps_thread(self):
        self.gps_thread = QThread()
        self.gps_worker = GpsWorker()
        self.gps_worker.moveToThread(self.gps_thread)
        self.gps_thread.started.connect(self.gps_worker.run)
        self.gps_worker.new_coordinates.connect(self.update_gps_marker)
        self.gps_thread.start()

    def search_location(self):
        if not self.map_loaded: return
        address = self.search_input.text()
        if not address: return
        self.status_label.setText("Buscando...")
        self.status_label.show()
        url = QUrl("https://nominatim.openstreetmap.org/search")
        url.setQuery(QUrl.fromPercentEncoding(f"q={address}&format=json&limit=1".encode()))
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader, "NemasWebCar/0.1")
        self.network_manager.get(request)

    @pyqtSlot("QNetworkReply*")
    def on_search_finished(self, reply):
        if reply.error():
            self.status_label.setText(f"Error de red: {reply.errorString()}")
            return
        data = reply.readAll().data()
        try:
            results = json.loads(data)
            if results:
                self.status_label.hide()
                self.status_label.setText("")
                location = results[0]
                lat, lon = float(location['lat']), float(location['lon'])
                display_name_js = location['display_name'].replace("'", "\\'")
                self.run_js(f"setMapView({lat}, {lon});")
                self.run_js(f"addMarker({lat}, {lon}, '{display_name_js}');")
            else:
                self.status_label.setText("Dirección no encontrada.")
        except json.JSONDecodeError:
            self.status_label.setText("Error al procesar la respuesta del servidor.")
        finally:
            reply.deleteLater()

    @pyqtSlot(float, float)
    def update_gps_marker(self, lat, lon):
        if not self.map_loaded: return
        self.run_js(f"updateGpsMarker({lat}, {lon});")

    def run_js(self, script):
        self.web_view.page().runJavaScript(script)

    def closeEvent(self, event):
        print("Cerrando el hilo de GPS...")
        self.gps_worker.running = False
        self.gps_thread.quit()
        self.gps_thread.wait()
        super().closeEvent(event)
