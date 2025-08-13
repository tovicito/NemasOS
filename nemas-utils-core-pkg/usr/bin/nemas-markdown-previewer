#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import markdown
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout,
    QTextEdit, QWebEngineView
)

class MarkdownPreviewerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visor de Markdown')
        self.setGeometry(100, 100, 1200, 700)

        layout = QHBoxLayout()

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Escribe tu Markdown aquí...")
        self.input_text.textChanged.connect(self.update_preview)

        self.preview_view = QWebEngineView()

        layout.addWidget(self.input_text, 1)
        layout.addWidget(self.preview_view, 1)

        self.setLayout(layout)

    def update_preview(self):
        md_text = self.input_text.toPlainText()
        html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
        self.preview_view.setHtml(html)

if __name__ == '__main__':
    # This utility requires python3-pyqt5.qtwebengine
    # and python3-markdown
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = MarkdownPreviewerGUI()
    ventana.show()
    sys.exit(app.exec_())
