#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QComboBox, QFileDialog
)

class FileChecksumGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculadora de Checksum para Archivos')
        self.setGeometry(300, 300, 500, 200)

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.file_label = QLabel("No se ha seleccionado ningún archivo.")
        self.browse_btn = QPushButton("Seleccionar Archivo...")
        self.browse_btn.clicked.connect(self.browse_file)

        self.combo_algo = QComboBox()
        self.combo_algo.addItems(["MD5", "SHA1", "SHA256", "SHA512"])

        self.output_hash = QLineEdit()
        self.output_hash.setReadOnly(True)

        form_layout.addWidget(self.browse_btn)
        form_layout.addWidget(QLabel("Algoritmo:"))
        form_layout.addWidget(self.combo_algo)

        layout.addWidget(self.file_label)
        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Resultado del Hash:"))
        layout.addWidget(self.output_hash)

        self.setLayout(layout)

    def browse_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo")
        if self.file_path:
            self.file_label.setText(f"Archivo: {self.file_path}")
            self.calculate_checksum()

    def calculate_checksum(self):
        if not self.file_path:
            return

        algo = self.combo_algo.currentText().lower()
        h = hashlib.new(algo)

        try:
            with open(self.file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    h.update(chunk)
            self.output_hash.setText(h.hexdigest())
        except Exception as e:
            self.output_hash.setText(f"Error: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = FileChecksumGUI()
    ventana.show()
    sys.exit(app.exec_())
