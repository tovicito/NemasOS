#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QStyle, QSlider
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class VideoPlayerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Reproductor de Video Simple')
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        video_widget = QVideoWidget()
        layout.addWidget(video_widget)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderMoved.connect(self.player.setPosition)

        self.player.positionChanged.connect(self.slider.setValue)
        self.player.durationChanged.connect(self.slider.setRange)
        self.player.setVideoOutput(video_widget)

        controls_layout = QHBoxLayout()
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)

        self.browse_btn = QPushButton("Abrir Video...")
        self.browse_btn.clicked.connect(self.browse_file)

        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.browse_btn)

        layout.addWidget(self.slider)
        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Video", "", "Video Files (*.mp4 *.avi *.mkv)")
        if file_path:
            url = QUrl.fromLocalFile(file_path)
            self.player.setMedia(QMediaContent(url))
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
    ventana = VideoPlayerGUI()
    ventana.show()
    sys.exit(app.exec_())
