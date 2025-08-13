#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QSpinBox, QLabel, QComboBox
)

class LoremIpsumGUI(QWidget):
    def __init__(self):
        super().__init__()
        # A basic lorem ipsum text
        self.lorem_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Generador de Lorem Ipsum')
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.combo_type = QComboBox()
        self.combo_type.addItems(["Palabras", "Frases", "Párrafos"])

        self.spin_amount = QSpinBox()
        self.spin_amount.setRange(1, 100)

        self.generate_btn = QPushButton("Generar")
        self.generate_btn.clicked.connect(self.generate_text)

        form_layout.addWidget(QLabel("Generar:"))
        form_layout.addWidget(self.spin_amount)
        form_layout.addWidget(self.combo_type)
        form_layout.addWidget(self.generate_btn)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        layout.addLayout(form_layout)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def generate_text(self):
        gen_type = self.combo_type.currentText()
        amount = self.spin_amount.value()

        words = self.lorem_text.split(' ')
        sentences = self.lorem_text.split('. ')

        result = ""
        if gen_type == "Palabras":
            result = " ".join(words[:amount])
        elif gen_type == "Frases":
            result = ". ".join(sentences[:amount])
        elif gen_type == "Párrafos":
            result = "\n\n".join([self.lorem_text] * amount)

        self.output_text.setText(result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = LoremIpsumGUI()
    ventana.show()
    sys.exit(app.exec_())
