#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QFileDialog, QListWidgetItem
)
from PyPDF2 import PdfFileMerger

class PdfMergerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Unificador de PDFs')
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        self.file_list = QListWidget()

        self.add_btn = QPushButton("Añadir PDFs...")
        self.add_btn.clicked.connect(self.add_files)

        self.remove_btn = QPushButton("Quitar Seleccionado")
        self.remove_btn.clicked.connect(self.remove_selected)

        self.merge_btn = QPushButton("Unir y Guardar...")
        self.merge_btn.clicked.connect(self.merge_files)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)

        layout.addWidget(self.file_list)
        layout.addLayout(btn_layout)
        layout.addWidget(self.merge_btn)

        self.setLayout(layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar PDFs", "", "PDF Files (*.pdf)")
        for file in files:
            self.file_list.addItem(QListWidgetItem(file))

    def remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def merge_files(self):
        if self.file_list.count() < 2:
            # Add message box
            return

        merger = PdfFileMerger()
        paths = [self.file_list.item(i).text() for i in range(self.file_list.count())]

        for path in paths:
            merger.append(path)

        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF Unificado", "", "PDF Files (*.pdf)")

        if save_path:
            try:
                with open(save_path, "wb") as fout:
                    merger.write(fout)
            except Exception as e:
                # Add error message box
                print(e)
            finally:
                merger.close()

if __name__ == '__main__':
    # Requires python3-pypdf2
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = PdfMergerGUI()
    ventana.show()
    sys.exit(app.exec_())
