#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
)
from PyQt5.QtCore import Qt

class DistractionFreeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Editor Sin Distracciones')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)

        self.text_area = QTextEdit()
        self.text_area.setStyleSheet("font-size: 16pt; border: none; padding: 20px;")

        self.fullscreen_button = QPushButton("Modo Pantalla Completa (F11)")
        self.fullscreen_button.setFocusPolicy(Qt.NoFocus) # Prevent button from taking focus
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        self.layout.addWidget(self.text_area)
        self.layout.addWidget(self.fullscreen_button)
        self.setLayout(self.layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_button.show()
        else:
            self.showFullScreen()
            self.fullscreen_button.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = DistractionFreeEditor()
    ventana.show()
    sys.exit(app.exec_())
