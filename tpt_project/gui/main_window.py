import sys

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLineEdit, QPushButton, QTableWidget, QTextEdit, QLabel, QSplitter
    )
    from PyQt6.QtCore import Qt
    HAS_PYQT6 = True
except ImportError:
    HAS_PYQT6 = False

from ..core.package_manager import PackageManager

class MainWindow(QMainWindow):
    """La ventana principal de la aplicación TPT GUI."""

    def __init__(self, pm: PackageManager):
        super().__init__()
        self.pm = pm

        if not HAS_PYQT6:
            # Esto no debería pasar si se comprueba antes, pero por si acaso.
            print("Error: PyQt6 no está instalado. La GUI no puede funcionar.", file=sys.stderr)
            sys.exit(1)

        self.setWindowTitle("TPT - La Herramienta de Paquetes Total")
        self.setGeometry(100, 100, 1200, 800)

        self._init_ui()

    def _init_ui(self):
        """Inicializa los widgets y el layout de la UI."""
        # --- Layouts Principales ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # --- Zona Superior: Búsqueda y Acciones ---
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar paquetes...")
        self.search_button = QPushButton("Buscar")
        self.upgrade_button = QPushButton("Actualizar Todo")

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_button)
        top_layout.addWidget(self.upgrade_button)

        # --- Zona Central: Resultados y Detalles ---
        center_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Widget para la tabla de resultados
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Nombre", "Versión", "Formato", "Descripción"])
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTriggers.NoEditTriggers)
        self.results_table.horizontalHeader().setStretchLastSection(True)

        # Widget para el panel de detalles
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        self.details_area = QTextEdit()
        self.details_area.setReadOnly(True)
        self.install_button = QPushButton("Instalar Paquete")
        details_layout.addWidget(QLabel("Detalles del Paquete:"))
        details_layout.addWidget(self.details_area)
        details_layout.addWidget(self.install_button)

        center_splitter.addWidget(self.results_table)
        center_splitter.addWidget(details_widget)
        center_splitter.setSizes([700, 500]) # Tamaños iniciales

        # --- Zona Inferior: Log ---
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0; font-family: 'Monospace';")
        self.log_console.setPlaceholderText("Aquí aparecerá el registro de actividad...")

        bottom_splitter = QSplitter(Qt.Orientation.Vertical)
        bottom_splitter.addWidget(center_splitter)
        bottom_splitter.addWidget(self.log_console)
        bottom_splitter.setSizes([600, 200])

        # --- Ensamblaje Final ---
        main_layout.addLayout(top_layout)
        main_layout.addWidget(bottom_splitter)

        # --- Conectar Señales (Lógica pendiente) ---
        # self.search_button.clicked.connect(self._on_search_clicked)
        # self.install_button.clicked.connect(self._on_install_clicked)
        # ...etc...

    def run(self):
        """Muestra la ventana y entra en el bucle de eventos."""
        self.show()

class GUI:
    """Clase controladora para la aplicación GUI."""
    def __init__(self, pm: PackageManager):
        if not HAS_PYQT6:
            raise ImportError("PyQt6 es necesario para la GUI. Por favor, instálalo con 'pip install PyQt6'.")

        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(pm)

    def run(self):
        self.main_window.run()
        sys.exit(self.app.exec())
