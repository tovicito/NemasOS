#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QStyle, QSlider
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class AudioPlayerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Reproductor de Audio Simple')
        self.setGeometry(300, 300, 400, 150)

        layout = QVBoxLayout()

        self.label_file = QLabel("No se ha seleccionado ningún archivo.")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderMoved.connect(self.player.setPosition)

        self.player.positionChanged.connect(self.slider.setValue)
        self.player.durationChanged.connect(self.slider.setRange)

        controls_layout = QHBoxLayout()
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_btn.clicked.connect(self.player.stop)

        self.browse_btn = QPushButton("Abrir Archivo...")
        self.browse_btn.clicked.connect(self.browse_file)

        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.browse_btn)

        layout.addWidget(self.label_file)
        layout.addWidget(self.slider)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo de Audio", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if file_path:
            url = QUrl.fromLocalFile(file_path)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.label_file.setText(f"Reproduciendo: {os.path.basename(file_path)}")
            self.player.play()

    def toggle_play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))


if __name__ == '__main__':
    import os
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = AudioPlayerGUI()
    ventana.show()
    sys.exit(app.exec_())
