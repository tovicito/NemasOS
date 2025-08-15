#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QLabel
)
from PyQt5.QtGui import QFont

class ChordFinderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.chords = {
            "C Major": "x32010",
            "G Major": "320003",
            "D Major": "xx0232",
            "A Major": "x02220",
            "E Major": "022100",
            "A Minor": "x02210",
            "E Minor": "022000",
            "D Minor": "xx0231"
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Buscador de Acordes de Guitarra')
        self.setGeometry(300, 300, 400, 400)
        layout = QVBoxLayout()
        controls_layout = QHBoxLayout()

        self.chord_combo = QComboBox()
        self.chord_combo.addItems(self.chords.keys())

        controls_layout.addWidget(QLabel("Acorde:"))
        controls_layout.addWidget(self.chord_combo)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        font = QFont("Monospace"); font.setStyleHint(QFont.TypeWriter)
        self.result_text.setFont(font)

        self.chord_combo.currentTextChanged.connect(self.update_display)

        layout.addLayout(controls_layout)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

        self.update_display()

    def generate_diagram(self, fingering):
        diagram = "e B G D A E\n"
        diagram += "------------\n"
        max_fret = 0
        for char in fingering:
            if char.isdigit():
                max_fret = max(max_fret, int(char))

        num_frets = max(4, max_fret + 1)

        for fret in range(1, num_frets + 1):
            line = ""
            for string_fret in fingering:
                if string_fret.isdigit() and int(string_fret) == fret:
                    line += "o "
                else:
                    line += "| "
            line += f" {fret}\n"
            diagram += line

        header = ""
        for char in fingering:
            if char == 'x':
                header += "x "
            elif char == '0':
                header += "o "
            else:
                header += "  "
        diagram = header + "\n" + diagram
        return diagram

    def update_display(self):
        chord_name = self.chord_combo.currentText()
        fingering = self.chords[chord_name]

        diagram = self.generate_diagram(fingering)

        display_text = f"Acorde: {chord_name}\n"
        display_text += f"Digitación: {fingering}\n\n"
        display_text += diagram

        self.result_text.setText(display_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ChordFinderGUI()
    ventana.show()
    sys.exit(app.exec_())
