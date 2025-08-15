#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QLabel
)
from PyQt5.QtGui import QFont

class ScaleReferenceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.scales = {
            "Major": "W-W-H-W-W-W-H",
            "Minor (Natural)": "W-H-W-W-H-W-W",
            "Minor (Harmonic)": "W-H-W-W-H-WH-H",
            "Minor (Melodic)": "W-H-W-W-W-W-H (Ascending)",
            "Major Pentatonic": "W-W-WH-W-WH",
            "Minor Pentatonic": "WH-W-W-WH-W",
            "Blues": "WH-W-H-H-WH-W"
        }
        self.notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Referencia de Escalas Musicales')
        self.setGeometry(300, 300, 500, 400)
        layout = QVBoxLayout()
        controls_layout = QHBoxLayout()

        self.key_combo = QComboBox()
        self.key_combo.addItems(self.notes)

        self.scale_combo = QComboBox()
        self.scale_combo.addItems(self.scales.keys())

        controls_layout.addWidget(QLabel("Tonalidad:"))
        controls_layout.addWidget(self.key_combo)
        controls_layout.addWidget(QLabel("Escala:"))
        controls_layout.addWidget(self.scale_combo)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        font = QFont("Monospace"); font.setStyleHint(QFont.TypeWriter)
        self.result_text.setFont(font)

        self.key_combo.currentTextChanged.connect(self.update_display)
        self.scale_combo.currentTextChanged.connect(self.update_display)

        layout.addLayout(controls_layout)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

        self.update_display()

    def calculate_scale(self, root_note, formula):
        scale_notes = [root_note]
        current_note_index = self.notes.index(root_note)

        step_map = {"W": 2, "H": 1, "WH": 3}

        steps = formula.split('-')
        for step in steps:
            current_note_index = (current_note_index + step_map[step]) % 12
            scale_notes.append(self.notes[current_note_index])

        return scale_notes

    def update_display(self):
        key = self.key_combo.currentText()
        scale_name = self.scale_combo.currentText()
        formula = self.scales[scale_name]

        notes_in_scale = self.calculate_scale(key, formula)

        display_text = f"Escala: {key} {scale_name}\n"
        display_text += f"Fórmula: {formula}\n\n"
        display_text += f"Notas: {' - '.join(notes_in_scale)}"

        self.result_text.setText(display_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ScaleReferenceGUI()
    ventana.show()
    sys.exit(app.exec_())
