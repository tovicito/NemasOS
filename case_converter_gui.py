#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton
)

class CaseConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Conversor de Mayúsculas/Minúsculas')
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Escribe o pega tu texto aquí")

        self.upper_btn = QPushButton("MAYÚSCULAS")
        self.lower_btn = QPushButton("minúsculas")
        self.title_btn = QPushButton("Título")
        self.sentence_btn = QPushButton("Oración")

        self.upper_btn.clicked.connect(self.convert_case)
        self.lower_btn.clicked.connect(self.convert_case)
        self.title_btn.clicked.connect(self.convert_case)
        self.sentence_btn.clicked.connect(self.convert_case)

        btn_layout.addWidget(self.upper_btn)
        btn_layout.addWidget(self.lower_btn)
        btn_layout.addWidget(self.title_btn)
        btn_layout.addWidget(self.sentence_btn)

        layout.addWidget(self.text_area)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def convert_case(self):
        sender = self.sender()
        current_text = self.text_area.toPlainText()

        if sender == self.upper_btn:
            new_text = current_text.upper()
        elif sender == self.lower_btn:
            new_text = current_text.lower()
        elif sender == self.title_btn:
            new_text = current_text.title()
        elif sender == self.sentence_btn:
            # Basic sentence case, capitalizes the first letter of each sentence.
            sentences = current_text.split('. ')
            new_sentences = [s.capitalize() for s in sentences]
            new_text = '. '.join(new_sentences)

        self.text_area.setText(new_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = CaseConverterGUI()
    ventana.show()
    sys.exit(app.exec_())
