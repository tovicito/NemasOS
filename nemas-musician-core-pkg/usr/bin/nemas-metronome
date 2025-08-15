#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtMultimedia import QSound

class MetronomeGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_tick)
        self.bpm = 120
        self.is_running = False

        # Simple tick sound - assuming a wav file is available
        # In a real scenario, we might generate a sound or package one.
        self.tick_sound = QSound("tick.wav", self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Metrónomo')
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()

        self.bpm_label = QLabel(f"{self.bpm} BPM")
        self.bpm_label.setAlignment(Qt.AlignCenter)
        font = self.bpm_label.font(); font.setPointSize(24); self.bpm_label.setFont(font)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(40, 240)
        self.slider.setValue(self.bpm)
        self.slider.valueChanged.connect(self.set_bpm)

        self.start_stop_btn = QPushButton("Iniciar")
        self.start_stop_btn.clicked.connect(self.toggle_metronome)

        layout.addWidget(self.bpm_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.start_stop_btn)
        self.setLayout(layout)

    def set_bpm(self, value):
        self.bpm = value
        self.bpm_label.setText(f"{self.bpm} BPM")
        if self.is_running:
            self.timer.setInterval(int(60000 / self.bpm))

    def toggle_metronome(self):
        if self.is_running:
            self.timer.stop()
            self.start_stop_btn.setText("Iniciar")
        else:
            self.timer.start(int(60000 / self.bpm))
            self.start_stop_btn.setText("Parar")
        self.is_running = not self.is_running

    def play_tick(self):
        # This will only work if a 'tick.wav' file is present.
        if self.tick_sound.isFinished():
            self.tick_sound.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Create a dummy tick.wav for testing
    import wave
    with wave.open('tick.wav', 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(1)
        f.setframerate(8000)
        f.writeframes(b'\x80\x00' * 100) # A simple click

    ventana = MetronomeGUI()
    ventana.show()
    sys.exit(app.exec_())
