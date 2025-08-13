#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import urllib.request
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel
)

class HttpHeaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visor de Cabeceras HTTP')
        self.setGeometry(300, 300, 600, 500)
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("ej. https://www.google.com")
        self.fetch_btn = QPushButton("Obtener Cabeceras")
        self.fetch_btn.clicked.connect(self.fetch_headers)

        form_layout.addWidget(QLabel("URL:"))
        form_layout.addWidget(self.url_edit)
        form_layout.addWidget(self.fetch_btn)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(form_layout)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

    def fetch_headers(self):
        url = self.url_edit.text()
        if not url.startswith('http'):
            url = 'http://' + url

        self.result_text.setText(f"Obteniendo cabeceras de {url}...")
        QApplication.processEvents()

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Nemas-OS-Utility'})
            with urllib.request.urlopen(req) as response:
                headers = response.info()
                self.result_text.setText(str(headers))
        except Exception as e:
            self.result_text.setText(f"Error: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = HttpHeaderGUI()
    ventana.show()
    sys.exit(app.exec_())
