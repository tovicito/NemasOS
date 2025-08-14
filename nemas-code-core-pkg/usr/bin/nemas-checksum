#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLineEdit, QLabel, QComboBox
)

class ChecksumGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculadora de Checksum para Texto')
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Pega el texto aquí...")

        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["MD5", "SHA1", "SHA256", "SHA512"])

        self.calc_btn = QPushButton("Calcular")
        self.calc_btn.clicked.connect(self.calculate_checksum)

        self.output_hash = QLineEdit()
        self.output_hash.setReadOnly(True)

        form_layout.addWidget(QLabel("Algoritmo:"))
        form_layout.addWidget(self.combo_algo)
        form_layout.addWidget(self.calc_btn)

        layout.addWidget(self.input_text)
        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Resultado del Hash:"))
        layout.addWidget(self.output_hash)

        self.setLayout(layout)

    def calculate_checksum(self):
        text = self.input_text.toPlainText().encode('utf-8')
        algo = self.combo_algo.currentText().lower()

        h = hashlib.new(algo)
        h.update(text)
        self.output_hash.setText(h.hexdigest())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ChecksumGUI()
    ventana.show()
    sys.exit(app.exec_())
