#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import whois
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel
)

class WhoisLookupGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Consulta WHOIS')
        self.setGeometry(300, 300, 600, 500)
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.domain_edit = QLineEdit()
        self.domain_edit.setPlaceholderText("ej. google.com")
        self.lookup_btn = QPushButton("Consultar")
        self.lookup_btn.clicked.connect(self.do_lookup)

        form_layout.addWidget(QLabel("Dominio:"))
        form_layout.addWidget(self.domain_edit)
        form_layout.addWidget(self.lookup_btn)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(form_layout)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

    def do_lookup(self):
        domain = self.domain_edit.text()
        if not domain:
            return

        self.result_text.setText(f"Consultando WHOIS para {domain}...")
        QApplication.processEvents()

        try:
            w = whois.whois(domain)
            self.result_text.setText(str(w))
        except Exception as e:
            self.result_text.setText(f"Error en la consulta: {e}")


if __name__ == '__main__':
    # Requires python3-whois
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = WhoisLookupGUI()
    ventana.show()
    sys.exit(app.exec_())
