#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import difflib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QWebEngineView
)

class DiffCheckerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Comparador de Texto (Diff)')
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()
        editors_layout = QHBoxLayout()

        self.text1 = QTextEdit()
        self.text1.setPlaceholderText("Texto A")
        self.text2 = QTextEdit()
        self.text2.setPlaceholderText("Texto B")

        editors_layout.addWidget(self.text1)
        editors_layout.addWidget(self.text2)

        self.compare_btn = QPushButton("Comparar Textos")
        self.compare_btn.clicked.connect(self.compare_text)

        self.result_view = QWebEngineView()

        layout.addLayout(editors_layout)
        layout.addWidget(self.compare_btn)
        layout.addWidget(self.result_view)

        self.setLayout(layout)

    def compare_text(self):
        text1_lines = self.text1.toPlainText().splitlines()
        text2_lines = self.text2.toPlainText().splitlines()

        d = difflib.HtmlDiff()
        html_diff = d.make_file(text1_lines, text2_lines, "Texto A", "Texto B")

        self.result_view.setHtml(html_diff)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = DiffCheckerGUI()
    ventana.show()
    sys.exit(app.exec_())
