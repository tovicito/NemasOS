#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import base64
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QButtonGroup
)

class Base64GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Codificador/Decodificador Base64')
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Texto de entrada")
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Texto de salida")
        self.output_text.setReadOnly(True)

        self.encode_btn = QPushButton("Codificar a Base64")
        self.decode_btn = QPushButton("Decodificar de Base64")

        self.encode_btn.clicked.connect(self.process_text)
        self.decode_btn.clicked.connect(self.process_text)

        btn_layout.addWidget(self.encode_btn)
        btn_layout.addWidget(self.decode_btn)

        layout.addWidget(self.input_text)
        layout.addLayout(btn_layout)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def process_text(self):
        sender = self.sender()
        input_str = self.input_text.toPlainText()

        try:
            if sender == self.encode_btn:
                output_str = base64.b64encode(input_str.encode('utf-8')).decode('utf-8')
            else: # decode
                output_str = base64.b64decode(input_str.encode('utf-8')).decode('utf-8')
            self.output_text.setText(output_str)
        except Exception as e:
            self.output_text.setText(f"Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = Base64GUI()
    ventana.show()
    sys.exit(app.exec_())
