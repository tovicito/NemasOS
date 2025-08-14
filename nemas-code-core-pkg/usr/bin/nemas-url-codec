#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from urllib.parse import quote, unquote
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton
)

class UrlCodecGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Codificador/Decodificador de URL')
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("URL o texto de entrada")
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("URL o texto de salida")
        self.output_text.setReadOnly(True)

        self.encode_btn = QPushButton("Codificar URL")
        self.decode_btn = QPushButton("Decodificar URL")

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
                output_str = quote(input_str)
            else: # decode
                output_str = unquote(input_str)
            self.output_text.setText(output_str)
        except Exception as e:
            self.output_text.setText(f"Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = UrlCodecGUI()
    ventana.show()
    sys.exit(app.exec_())
