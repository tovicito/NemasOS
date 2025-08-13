#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QTextEdit, QFontDatabase
)

class HexViewerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visor Hexadecimal')
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Escribe texto para ver su representación hexadecimal...")
        self.input_text.textChanged.connect(self.update_hex_view)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        # Use a monospace font for better alignment
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.output_text.setFont(font)

        layout.addWidget(self.input_text)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def update_hex_view(self):
        text = self.input_text.toPlainText()
        try:
            # Convert string to hex representation
            hex_str = text.encode('utf-8').hex(' ')
            self.output_text.setText(hex_str)
        except Exception as e:
            self.output_text.setText(f"Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = HexViewerGUI()
    ventana.show()
    sys.exit(app.exec_())
