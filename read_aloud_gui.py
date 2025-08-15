#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pyttsx3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTextEdit
)

class ReadAloudGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Lector de Texto (Read-Aloud)')
        self.setGeometry(300, 300, 500, 400)
        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Escribe o pega el texto que quieres escuchar...")

        self.read_btn = QPushButton("Leer Texto")
        self.read_btn.clicked.connect(self.read_text)

        self.stop_btn = QPushButton("Parar")
        self.stop_btn.clicked.connect(self.stop_reading)

        layout.addWidget(self.text_area)
        layout.addWidget(self.read_btn)
        layout.addWidget(self.stop_btn)
        self.setLayout(layout)

    def read_text(self):
        text = self.text_area.toPlainText()
        if text:
            self.engine.say(text)
            self.engine.runAndWait()

    def stop_reading(self):
        self.engine.stop()

    def closeEvent(self, event):
        self.engine.stop()
        event.accept()


if __name__ == '__main__':
    # Requires python3-pyttsx3
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ReadAloudGUI()
    ventana.show()
    sys.exit(app.exec_())
