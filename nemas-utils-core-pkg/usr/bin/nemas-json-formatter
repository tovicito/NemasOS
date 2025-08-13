#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QTextEdit, QPushButton, QLabel
)
from PyQt5.QtGui import QColor

class JsonFormatterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Formateador y Validador JSON')
        self.setGeometry(300, 300, 700, 600)

        layout = QVBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Pega tu JSON aquí...")

        self.format_btn = QPushButton("Formatear / Validar JSON")
        self.format_btn.clicked.connect(self.format_json)

        self.status_label = QLabel("Estado: Esperando entrada")

        layout.addWidget(self.input_text)
        layout.addWidget(self.format_btn)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def format_json(self):
        input_str = self.input_text.toPlainText()
        try:
            json_obj = json.loads(input_str)
            formatted_json = json.dumps(json_obj, indent=4, sort_keys=True)
            self.input_text.setText(formatted_json)
            self.status_label.setText("Estado: JSON Válido y Formateado")
            self.status_label.setStyleSheet("color: green;")
        except json.JSONDecodeError as e:
            self.status_label.setText(f"Estado: Error de JSON - {e}")
            self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            self.status_label.setText(f"Estado: Error - {e}")
            self.status_label.setStyleSheet("color: red;")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = JsonFormatterGUI()
    ventana.show()
    sys.exit(app.exec_())
