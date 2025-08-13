#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel, QColorDialog
)
from PyQt5.QtGui import QColor, QPixmap

class ColorPickerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Selector de Color')
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()

        self.pick_btn = QPushButton("Seleccionar un Color")
        self.pick_btn.clicked.connect(self.pick_color)

        self.color_swatch = QLabel()
        self.color_swatch.setMinimumHeight(50)

        self.color_label = QLabel("Hex: #ffffff | RGB: (255, 255, 255)")

        layout.addWidget(self.pick_btn)
        layout.addWidget(self.color_swatch)
        layout.addWidget(self.color_label)
        self.setLayout(layout)

        self.set_swatch_color(QColor(255, 255, 255))

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_swatch_color(color)

    def set_swatch_color(self, color):
        pixmap = QPixmap(self.color_swatch.width(), self.color_swatch.height())
        pixmap.fill(color)
        self.color_swatch.setPixmap(pixmap)

        hex_code = color.name().upper()
        rgb_code = f"({color.red()}, {color.green()}, {color.blue()})"
        self.color_label.setText(f"Hex: {hex_code} | RGB: {rgb_code}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ColorPickerGUI()
    ventana.show()
    sys.exit(app.exec_())
