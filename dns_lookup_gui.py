#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel
)

class DnsLookupGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Consulta DNS')
        self.setGeometry(300, 300, 500, 300)
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("ej. www.google.com")
        self.lookup_btn = QPushButton("Consultar")
        self.lookup_btn.clicked.connect(self.do_lookup)

        form_layout.addWidget(QLabel("Host:"))
        form_layout.addWidget(self.host_edit)
        form_layout.addWidget(self.lookup_btn)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(form_layout)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

    def do_lookup(self):
        host = self.host_edit.text()
        if not host:
            return

        self.result_text.setText(f"Consultando DNS para {host}...")
        QApplication.processEvents()

        try:
            ip_address = socket.gethostbyname(host)
            self.result_text.setText(f"La dirección IP para {host} es: {ip_address}")
        except socket.gaierror as e:
            self.result_text.setText(f"No se pudo resolver el host: {e}")
        except Exception as e:
            self.result_text.setText(f"Ocurrió un error: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = DnsLookupGUI()
    ventana.show()
    sys.exit(app.exec_())
