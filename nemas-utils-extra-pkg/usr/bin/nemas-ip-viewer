#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import socket
import urllib.request
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel, QLineEdit
)

class IpViewerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visor de Dirección IP')
        self.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout()

        self.local_ip_label = QLabel("IP Local:")
        self.local_ip_edit = QLineEdit()
        self.local_ip_edit.setReadOnly(True)

        self.public_ip_label = QLabel("IP Pública:")
        self.public_ip_edit = QLineEdit()
        self.public_ip_edit.setReadOnly(True)

        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.clicked.connect(self.get_ips)

        layout.addWidget(self.local_ip_label)
        layout.addWidget(self.local_ip_edit)
        layout.addWidget(self.public_ip_label)
        layout.addWidget(self.public_ip_edit)
        layout.addWidget(self.refresh_btn)
        self.setLayout(layout)

        self.get_ips()

    def get_ips(self):
        # Get Local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            self.local_ip_edit.setText(local_ip)
        except Exception as e:
            self.local_ip_edit.setText(f"Error: {e}")

        # Get Public IP
        self.public_ip_edit.setText("Obteniendo...")
        QApplication.processEvents()
        try:
            public_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
            self.public_ip_edit.setText(public_ip)
        except Exception as e:
            self.public_ip_edit.setText("No se pudo obtener la IP pública")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = IpViewerGUI()
    ventana.show()
    sys.exit(app.exec_())
