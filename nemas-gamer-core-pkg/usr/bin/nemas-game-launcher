#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QInputDialog
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

class GameLauncherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.games_db = "games.json"
        self.games = self.load_games()
        self.initUI()

    def load_games(self):
        try:
            with open(self.games_db, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_games(self):
        with open(self.games_db, 'w') as f:
            json.dump(self.games, f, indent=4)

    def initUI(self):
        self.setWindowTitle('Lanzador de Juegos Simple')
        self.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()

        self.game_list = QListWidget()
        self.game_list.setViewMode(QListWidget.IconMode)
        self.game_list.setIconSize(QSize(64, 64))
        self.game_list.itemDoubleClicked.connect(self.launch_game)
        self.populate_list()

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Añadir Juego...")
        self.remove_btn = QPushButton("Quitar Juego")

        self.add_btn.clicked.connect(self.add_game)
        self.remove_btn.clicked.connect(self.remove_game)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)

        layout.addWidget(self.game_list)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def populate_list(self):
        self.game_list.clear()
        for game in self.games:
            item = QListWidgetItem(QIcon.fromTheme("applications-games"), game['name'])
            self.game_list.addItem(item)

    def add_game(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Ejecutable del Juego")
        if not path: return

        name, ok = QInputDialog.getText(self, 'Nombre del Juego', 'Introduce un nombre para el juego:')
        if ok and name:
            self.games.append({"name": name, "path": path})
            self.save_games()
            self.populate_list()

    def remove_game(self):
        selected = self.game_list.currentItem()
        if not selected: return

        # This is a simple implementation, assumes names are unique
        self.games = [g for g in self.games if g['name'] != selected.text()]
        self.save_games()
        self.populate_list()

    def launch_game(self, item):
        game_path = None
        for game in self.games:
            if game['name'] == item.text():
                game_path = game['path']
                break

        if game_path:
            try:
                subprocess.Popen([game_path])
            except Exception as e:
                print(f"Error launching game: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = GameLauncherGUI()
    ventana.show()
    sys.exit(app.exec_())
