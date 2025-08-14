#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QSpinBox
)

class PingToolGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Herramienta de Ping')
        self.setGeometry(300, 300, 500, 400)
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("ej. google.com")
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 20); self.count_spin.setValue(4)

        form_layout.addWidget(QLabel("Host:"))
        form_layout.addWidget(self.host_edit)
        form_layout.addWidget(QLabel("Nº de pings:"))
        form_layout.addWidget(self.count_spin)

        self.ping_btn = QPushButton("Hacer Ping")
        self.ping_btn.clicked.connect(self.do_ping)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(form_layout)
        layout.addWidget(self.ping_btn)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

    def do_ping(self):
        host = self.host_edit.text()
        count = self.count_spin.value()
        if not host:
            return

        self.result_text.setText(f"Haciendo ping a {host} {count} veces...")
        QApplication.processEvents()

        try:
            command = ["ping", "-c", str(count), host]
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                self.result_text.setText(result.stdout)
            else:
                self.result_text.setText(result.stderr)
        except Exception as e:
            self.result_text.setText(f"Error al ejecutar el comando ping: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = PingToolGUI()
    ventana.show()
    sys.exit(app.exec_())
