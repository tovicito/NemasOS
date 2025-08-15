#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QListWidget, QLabel
)

class ThesaurusGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Tesauro')
        self.setGeometry(300, 300, 400, 500)
        layout = QVBoxLayout()
        search_layout = QHBoxLayout()

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Introduce una palabra...")
        self.search_btn = QPushButton("Buscar Sinónimos")
        self.search_btn.clicked.connect(self.find_synonyms)

        search_layout.addWidget(self.word_input)
        search_layout.addWidget(self.search_btn)

        self.result_list = QListWidget()

        layout.addLayout(search_layout)
        layout.addWidget(QLabel("Resultados:"))
        layout.addWidget(self.result_list)
        self.setLayout(layout)

    def find_synonyms(self):
        word = self.word_input.text()
        if not word:
            return

        self.result_list.clear()
        self.result_list.addItem("Buscando...")
        QApplication.processEvents()

        try:
            # Using Datamuse API
            response = requests.get(f'https://api.datamuse.com/words?rel_syn={word}')
            response.raise_for_status()
            results = response.json()

            self.result_list.clear()
            if not results:
                self.result_list.addItem("No se encontraron sinónimos.")
            else:
                for item in results:
                    self.result_list.addItem(item['word'])

        except requests.exceptions.RequestException as e:
            self.result_list.clear()
            self.result_list.addItem(f"Error de red: {e}")
        except Exception as e:
            self.result_list.clear()
            self.result_list.addItem(f"Error: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ThesaurusGUI()
    ventana.show()
    sys.exit(app.exec_())
