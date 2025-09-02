import os
# This file had its constants removed and logic fixed in a previous step that failed to apply.
# This patch is intended to be applied to the original file content.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QLabel, QSlider, QFileDialog, QListWidgetItem)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QFont
from nemas_webcar.style import *

class MusicPage(QWidget):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.playlist = []
        self.current_index = -1

        self.setFont(QFont(KIA_FONT_FAMILY))
        self.setStyleSheet(f"""
            QLabel {{ color: {KIA_LIGHT_GREY}; }}
            QPushButton {{
                background-color: {KIA_DARK_GREY};
                color: {KIA_LIGHT_GREY};
                border: 1px solid {KIA_HOVER_GREY};
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {KIA_HOVER_GREY}; }}
            #AddFolderButton {{
                background-color: {KIA_VIOLET};
                color: {KIA_BLACK};
                border: none;
            }}
            #AddFolderButton:hover {{ background-color: {KIA_VIOLET_LIGHT}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        title = QLabel("Reproductor de Música")
        title.setFont(QFont(KIA_FONT_FAMILY, 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {KIA_LIGHT_GREY}; margin-bottom: 20px;")
        layout.addWidget(title)

        self.playlist_widget = QListWidget()
        self.playlist_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {KIA_DARK_GREY};
                border: none;
                border-radius: 8px;
                color: {KIA_LIGHT_GREY};
                padding: 5px;
            }}
            QListWidget::item {{ padding: 10px; }}
            QListWidget::item:hover {{ background-color: {KIA_HOVER_GREY}; border-radius: 5px; }}
            QListWidget::item:selected {{ background-color: {KIA_VIOLET}; color: {KIA_BLACK}; border-radius: 5px;}}
        """)
        layout.addWidget(self.playlist_widget)

        self.current_song_label = QLabel("Ninguna canción seleccionada")
        self.current_song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_song_label.setFont(QFont(KIA_FONT, 14, QFont.Weight.Bold))
        layout.addWidget(self.current_song_label)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {KIA_DARK_GREY};
                height: 4px;
                background: {KIA_DARK_GREY};
                margin: 2px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {KIA_VIOLET};
                border: 1px solid {KIA_VIOLET};
                width: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }}
        """)
        self.progress_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.progress_slider)

        controls_layout = QHBoxLayout()
        self.play_pause_button = QPushButton("Play")
        self.prev_button = QPushButton("Anterior")
        self.next_button = QPushButton("Siguiente")
        self.add_folder_button = QPushButton("Añadir Carpeta")
        self.add_folder_button.setObjectName("AddFolderButton")

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addWidget(self.next_button)
        layout.addLayout(controls_layout)
        layout.addWidget(self.add_folder_button)

        # Connect Signals
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.prev_button.clicked.connect(self.play_prev)
        self.next_button.clicked.connect(self.play_next)
        self.add_folder_button.clicked.connect(self.add_music_folder)
        self.playlist_widget.itemDoubleClicked.connect(self.play_song_from_list)

        self.player.positionChanged.connect(self.update_slider)
        self.player.durationChanged.connect(self.update_slider_range)
        self.player.mediaStatusChanged.connect(self.handle_media_status)

    def add_music_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Música")
        if folder:
            for file in os.listdir(folder):
                if file.lower().endswith(('.mp3', '.flac', '.wav', '.m4a')):
                    path = os.path.join(folder, file)
                    self.playlist.append(path)
                    item = QListWidgetItem(os.path.basename(path))
                    self.playlist_widget.addItem(item)

    def play_song_from_list(self, item):
        self.current_index = self.playlist_widget.row(item)
        self.play_current_song()

    def play_current_song(self):
        if 0 <= self.current_index < len(self.playlist):
            path = self.playlist[self.current_index]
            self.player.setSource(QUrl.fromLocalFile(path))
            self.player.play()
            self.play_pause_button.setText("Pause")
            self.current_song_label.setText(os.path.basename(path))

    def toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_pause_button.setText("Play")
        else:
            self.player.play()
            self.play_pause_button.setText("Pause")

    def update_slider(self, position):
        if self.progress_slider.isSliderDown() == False:
            self.progress_slider.setValue(position)

    def update_slider_range(self, duration):
        self.progress_slider.setRange(0, duration)

    def set_position(self, position):
        self.player.setPosition(position)

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self.player.source() != QUrl():
            self.play_next()

    def play_next(self):
        if self.playlist:
            # Fixed logic as per code review
            self.current_index = (self.current_index - 1 + len(self.playlist)) % len(self.playlist)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.play_current_song()

    def play_prev(self):
        if self.playlist:
            # Fixed logic as per code review
            self.current_index = (self.current_index - 1 + len(self.playlist)) % len(self.playlist)
            self.playlist_widget.setCurrentRow(self.current_index)
            self.play_current_song()
