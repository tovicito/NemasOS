#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# contador_caracteres_gui.py - A GUI utility to count characters, words, and lines.
#

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton
)
from PyQt5.QtCore import Qt

class ContadorCaracteresGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Contador de Caracteres, Palabras y Líneas')
        self.setGeometry(300, 300, 500, 400)

        # Layouts
        main_layout = QVBoxLayout()
        stats_layout = QHBoxLayout()

        # Text Area
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Pega o escribe tu texto aquí...")
        self.text_area.textChanged.connect(self.update_stats)
        main_layout.addWidget(self.text_area)

        # Stats Labels
        self.label_chars = QLabel("Caracteres: 0")
        self.label_words = QLabel("Palabras: 0")
        self.label_lines = QLabel("Líneas: 0")

        stats_layout.addWidget(self.label_chars)
        stats_layout.addStretch(1)
        stats_layout.addWidget(self.label_words)
        stats_layout.addStretch(1)
        stats_layout.addWidget(self.label_lines)

        main_layout.addLayout(stats_layout)

        # Clear Button
        clear_button = QPushButton("Limpiar")
        clear_button.clicked.connect(self.clear_text)
        main_layout.addWidget(clear_button)

        self.setLayout(main_layout)

    def update_stats(self):
        text = self.text_area.toPlainText()

        # Character count
        char_count = len(text)
        self.label_chars.setText(f"Caracteres: {char_count}")

        # Word count
        words = text.split()
        word_count = len(words)
        self.label_words.setText(f"Palabras: {word_count}")

        # Line count
        line_count = text.count('\n') + 1 if text else 0
        self.label_lines.setText(f"Líneas: {line_count}")

    def clear_text(self):
        self.text_area.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ContadorCaracteresGUI()
    ventana.show()
    sys.exit(app.exec_())
