import os
import json
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
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

# --- GPS Worker Thread ---
class GpsWorker(QObject):
    """
    Worker that runs in a separate thread to poll for GPS data
    without freezing the UI.
    """
    new_coordinates = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.running = True

    @pyqtSlot()
    def run(self):
        """Main polling loop."""
        if not GPSD_AVAILABLE:
            return

        try:
            gpsd.connect()
        except Exception as e:
            print(f"Error al conectar con gpsd: {e}. El hilo de GPS no se iniciará.")
            return

        while self.running:
            try:
                packet = gpsd.get_current()
                if packet.mode >= 2: # Mode 2 is 2D fix, Mode 3 is 3D fix
                    lat, lon = packet.lat, packet.lon
                    self.new_coordinates.emit(lat, lon)
            except Exception as e:
                print(f"Error en el bucle de GPS: {e}")
                # Wait a bit before retrying to avoid spamming errors
                time.sleep(5)

            time.sleep(2) # Poll every 2 seconds

# --- Map Page Widget ---
class MapPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setFont(QFont(KIA_FONT_FAMILY))

        # --- Main Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Search Bar Layout ---
        search_bar_widget = QWidget()
        search_bar_widget.setStyleSheet(f"background-color: {KIA_DARK_GREY};")
        search_bar_layout = QHBoxLayout(search_bar_widget)
        search_bar_layout.setContentsMargins(15, 15, 15, 15)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar dirección...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {KIA_HOVER_GREY};
                border-radius: 8px;
                padding: 10px;
                background-color: {KIA_BLACK};
                color: {KIA_LIGHT_GREY};
                font-size: 16px;
            }}
        """)

        self.search_button = QPushButton("Buscar")
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {KIA_VIOLET};
                color: {KIA_BLACK};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {KIA_VIOLET_LIGHT};
            }}
        """)

        search_bar_layout.addWidget(self.search_input)
        search_bar_layout.addWidget(self.search_button)
        layout.addWidget(search_bar_widget)

        # --- Web View ---
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # --- Network Manager for API calls ---
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_search_finished)

        # --- Connections ---
        self.search_button.clicked.connect(self.search_location)
        self.search_input.returnPressed.connect(self.search_location)

        # --- Load Map ---
        html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'map.html'))
        self.web_view.setUrl(QUrl.fromLocalFile(html_file_path))

        # --- GPS Thread Setup ---
        self.setup_gps_thread()

    def setup_gps_thread(self):
        self.gps_thread = QThread()
        self.gps_worker = GpsWorker()
        self.gps_worker.moveToThread(self.gps_thread)

        # Connect signals and slots
        self.gps_thread.started.connect(self.gps_worker.run)
        self.gps_worker.new_coordinates.connect(self.update_gps_marker)

        # Start the thread
        self.gps_thread.start()

    def search_location(self):
        # ... (search logic remains the same)
        address = self.search_input.text()
        if not address: return
        url = QUrl("https://nominatim.openstreetmap.org/search")
        query = QUrl.fromPercentEncoding(f"q={address}&format=json&limit=1".encode())
        url.setQuery(query)
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader, "NemasWebCar/0.1")
        self.network_manager.get(request)

    @pyqtSlot("QNetworkReply*")
    def on_search_finished(self, reply):
        # ... (search handling remains the same)
        if reply.error():
            print(f"Error en la petición: {reply.errorString()}")
            return
        data = reply.readAll().data()
        try:
            results = json.loads(data)
            if results:
                location = results[0]
                lat, lon = float(location['lat']), float(location['lon'])
                display_name_js = location['display_name'].replace("'", "\\'")
                # Removed hardcoded zoom as per code review
                self.run_js(f"setMapView({lat}, {lon});")
                self.run_js(f"addMarker({lat}, {lon}, '{display_name_js}');")
        except json.JSONDecodeError:
            print("Error decodificando la respuesta JSON.")
        finally:
            reply.deleteLater()

    @pyqtSlot(float, float)
    def update_gps_marker(self, lat, lon):
        """Slot to receive GPS coordinates and update the map."""
        self.run_js(f"updateGpsMarker({lat}, {lon});")

    def run_js(self, script):
        self.web_view.page().runJavaScript(script)

    def closeEvent(self, event):
        """Ensure the GPS thread is stopped cleanly."""
        print("Cerrando el hilo de GPS...")
        self.gps_worker.running = False
        self.gps_thread.quit()
        self.gps_thread.wait()
        super().closeEvent(event)
