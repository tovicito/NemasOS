import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

# Import the new pages
from app.settings_page import SettingsPage
from app.map_page import MapPage
from app.music_page import MusicPage

# Import shared style constants
from nemas_webcar.style import *

# A simple placeholder widget for our app pages
class Page(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont(KIA_FONT_FAMILY, 24))
        self.setStyleSheet(f"color: {KIA_LIGHT_GREY};")

class NemasWebCar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nemas WebCar")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet(f"background-color: {KIA_BLACK}; font-family: {KIA_FONT_FAMILY};")

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Navigation Bar ---
        nav_bar = QWidget()
        nav_bar.setStyleSheet(f"background-color: {KIA_DARK_GREY};")
        nav_layout = QVBoxLayout(nav_bar)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(5, 20, 5, 20)

        self.nav_buttons = []
        app_icons = ["map.svg", "music.svg", "settings.svg", "smartphone.svg"]

        for icon_file in app_icons:
            button = QPushButton()
            icon_path = f"nemas_webcar/icons/{icon_file}"
            # Simplified icon loading as per code review
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(32, 32))
            button.setCheckable(True)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    padding: 15px;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {KIA_HOVER_GREY};
                }}
                QPushButton:checked {{
                    background-color: {KIA_VIOLET};
                }}
            """)
            self.nav_buttons.append(button)
            nav_layout.addWidget(button)

        # --- Content Area ---
        self.content_area = QStackedWidget()

        self.content_area.addWidget(MapPage())
        self.content_area.addWidget(MusicPage())
        self.content_area.addWidget(SettingsPage())
        # The placeholder page for Android Auto will now also have the new style
        self.content_area.addWidget(Page("Función no disponible"))

        main_layout.addWidget(nav_bar, 1)
        main_layout.addWidget(self.content_area, 6) # Give content more space

        # --- Connect signals ---
        for i, button in enumerate(self.nav_buttons):
            button.clicked.connect(lambda checked, index=i: self.switch_page(index))

        # Select the first page by default
        self.nav_buttons[0].setChecked(True)
        self.switch_page(0)

    def switch_page(self, index):
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)
        self.content_area.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setOrganizationName("Nemas")
    app.setApplicationName("NemasWebCar")

    main_window = NemasWebCar()
    main_window.show()
    sys.exit(app.exec())
