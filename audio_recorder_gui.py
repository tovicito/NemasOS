#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pyaudio
import wave
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel
)
from PyQt5.QtCore import QTimer

class AudioRecorderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.record_time = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Grabadora de Audio Simple')
        self.setGeometry(300, 300, 300, 150)
        layout = QVBoxLayout()

        self.status_label = QLabel("Listo para grabar")
        self.record_btn = QPushButton("Grabar")
        self.record_btn.clicked.connect(self.toggle_recording)

        layout.addWidget(self.status_label)
        layout.addWidget(self.record_btn)
        self.setLayout(layout)

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.frames = []
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=44100,
                                  input=True,
                                  frames_per_buffer=1024)
        self.is_recording = True
        self.record_time = 0
        self.timer.start(1000)
        self.record_btn.setText("Parar")
        self.status_label.setText("Grabando...")

    def stop_recording(self):
        self.is_recording = False
        self.timer.stop()
        self.record_btn.setText("Grabar")
        self.status_label.setText("Grabación finalizada.")

        self.stream.stop_stream()
        self.stream.close()

        self.save_file()

    def save_file(self):
        filename = "recording.wav" # Simple default
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        self.status_label.setText(f"Grabación guardada en {filename}")

    def update_status(self):
        if self.is_recording:
            self.record_time += 1
            self.status_label.setText(f"Grabando... {self.record_time}s")
            # Append audio data
            data = self.stream.read(1024)
            self.frames.append(data)

    def closeEvent(self, event):
        if self.stream is not None:
            self.stream.close()
        self.p.terminate()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = AudioRecorderGUI()
    ventana.show()
    sys.exit(app.exec_())
