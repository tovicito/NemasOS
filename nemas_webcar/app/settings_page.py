from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QCheckBox, QComboBox, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
from nemas_webcar.style import *

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setFont(QFont(KIA_FONT_FAMILY))
        self.setStyleSheet(f"""
            QWidget {{
                color: {KIA_LIGHT_GREY};
                font-size: 16px;
            }}
            QLineEdit, QComboBox {{
                border: 1px solid {KIA_HOVER_GREY};
                border-radius: 8px;
                padding: 10px;
                background-color: {KIA_DARK_GREY};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QPushButton {{
                background-color: {KIA_VIOLET};
                color: {KIA_BLACK};
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {KIA_VIOLET_LIGHT};
            }}
            QLabel {{
                font-weight: bold;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 5px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {KIA_DARK_GREY};
                border: 1px solid {KIA_HOVER_GREY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {KIA_VIOLET};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)

        title_label = QLabel("Configuración del Sistema")
        title_label.setFont(QFont(KIA_FONT_FAMILY, 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {KIA_LIGHT_GREY}; margin-bottom: 20px;")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(20)

        self.username_input = QLineEdit()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Español", "English", "Français"])
        self.dark_mode_check = QCheckBox("Habilitar Paper GUI")
        self.dark_mode_check.setChecked(True)

        form_layout.addRow(QLabel("Nombre de Usuario:"), self.username_input)
        form_layout.addRow(QLabel("Idioma:"), self.language_combo)
        form_layout.addRow(self.dark_mode_check)

        layout.addLayout(form_layout)
        layout.addStretch(1)

        self.save_button = QPushButton("Guardar Cambios")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.load_settings()

    def save_settings(self):
        settings = QSettings()
        settings.setValue("username", self.username_input.text())
        settings.setValue("language", self.language_combo.currentText())
        settings.setValue("paperMode", self.dark_mode_check.isChecked())
        print("Settings saved!")

    def load_settings(self):
        settings = QSettings()
        username = settings.value("username", "Nemas User")
        language = settings.value("language", "Español")
        paper_mode = settings.value("paperMode", True, type=bool)

        self.username_input.setText(username)
        self.language_combo.setCurrentText(language)
        self.dark_mode_check.setChecked(paper_mode)
        print("Settings loaded!")
