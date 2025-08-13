#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QLabel
)

class FileEncryptorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Cifrador/Descifrador de Archivos (XOR)')
        self.setGeometry(300, 300, 500, 200)
        layout = QVBoxLayout()

        self.file_label = QLabel("Selecciona un archivo...")
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Clave de cifrado")

        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Seleccionar Archivo")
        self.encrypt_btn = QPushButton("Cifrar")
        self.decrypt_btn = QPushButton("Descifrar")

        self.select_btn.clicked.connect(self.select_file)
        self.encrypt_btn.clicked.connect(self.process_file)
        self.decrypt_btn.clicked.connect(self.process_file)

        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.encrypt_btn)
        btn_layout.addWidget(self.decrypt_btn)

        layout.addWidget(self.file_label)
        layout.addWidget(QLabel("Clave:"))
        layout.addWidget(self.key_edit)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.input_file = None

    def select_file(self):
        self.input_file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo")
        if self.input_file:
            self.file_label.setText(f"Archivo: {self.input_file}")

    def process_file(self):
        if not self.input_file or not self.key_edit.text():
            self.file_label.setText("Error: Selecciona un archivo y una clave.")
            return

        key = self.key_edit.text().encode('utf-8')

        try:
            with open(self.input_file, 'rb') as f_in:
                data = f_in.read()

            processed_data = bytearray()
            for i in range(len(data)):
                processed_data.append(data[i] ^ key[i % len(key)])

            save_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo Procesado")
            if save_path:
                with open(save_path, 'wb') as f_out:
                    f_out.write(processed_data)
                self.file_label.setText(f"¡Éxito! Archivo guardado en {save_path}")

        except Exception as e:
            self.file_label.setText(f"Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = FileEncryptorGUI()
    ventana.show()
    sys.exit(app.exec_())
