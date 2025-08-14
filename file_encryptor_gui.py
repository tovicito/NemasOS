#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel
)
from PyQt5.QtCore import Qt

class PlaceholderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # The window title will be set by the script that calls this
        self.setWindowTitle('Nemás Utility')
        self.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(self)

        label = QLabel("Esta utilidad aún no ha sido implementada.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # The title can be passed as an argument
    title = sys.argv[1] if len(sys.argv) > 1 else "Nemás Utility"
    app.setStyle('Fusion')
    ventana = PlaceholderWindow()
    ventana.setWindowTitle(title)
    ventana.show()
    sys.exit(app.exec_())
