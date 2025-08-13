#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QSpinBox
)

class PortScannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Escáner de Puertos')
        self.setGeometry(300, 300, 500, 400)
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("ej. 127.0.0.1 o google.com")
        self.start_port_spin = QSpinBox()
        self.start_port_spin.setRange(1, 65535); self.start_port_spin.setValue(1)
        self.end_port_spin = QSpinBox()
        self.end_port_spin.setRange(1, 65535); self.end_port_spin.setValue(1024)

        form_layout.addWidget(QLabel("Host:"))
        form_layout.addWidget(self.host_edit)
        form_layout.addWidget(QLabel("Desde:"))
        form_layout.addWidget(self.start_port_spin)
        form_layout.addWidget(QLabel("Hasta:"))
        form_layout.addWidget(self.end_port_spin)

        self.scan_btn = QPushButton("Escanear Puertos")
        self.scan_btn.clicked.connect(self.scan_ports)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(form_layout)
        layout.addWidget(self.scan_btn)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

    def scan_ports(self):
        host = self.host_edit.text()
        start_port = self.start_port_spin.value()
        end_port = self.end_port_spin.value()

        if not host:
            self.result_text.setText("Por favor, introduce un host.")
            return

        self.result_text.setText(f"Escaneando {host} desde el puerto {start_port} hasta {end_port}...\n")
        QApplication.processEvents()

        try:
            target = socket.gethostbyname(host)
        except socket.gaierror:
            self.result_text.append("Error: No se pudo resolver el nombre del host.")
            return

        for port in range(start_port, end_port + 1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(0.1)
            result = s.connect_ex((target, port))
            if result == 0:
                self.result_text.append(f"Puerto {port}: Abierto\n")
            s.close()
            QApplication.processEvents()

        self.result_text.append("\nEscaneo completado.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = PortScannerGUI()
    ventana.show()
    sys.exit(app.exec_())
