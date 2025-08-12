#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# editor_texto_gui.py - Un editor de texto simple con GUI (Nemás OS)
#

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStatusBar, QAction,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIcon, QKeySequence

class EditorTextoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ruta_archivo_actual = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Editor de Texto - Sin Título")
        self.setGeometry(100, 100, 800, 600)

        # Widget central de texto
        self.editor = QTextEdit()
        self.editor.textChanged.connect(lambda: self.setWindowModified(True))
        self.setCentralWidget(self.editor)

        # Barra de estado
        self.setStatusBar(QStatusBar(self))
        self.editor.cursorPositionChanged.connect(self.actualizar_estado)

        # --- Acciones ---
        accion_nuevo = QAction("Nuevo", self, shortcut=QKeySequence.New, triggered=self.nuevo_archivo)
        accion_abrir = QAction("Abrir...", self, shortcut=QKeySequence.Open, triggered=self.abrir_archivo)
        accion_guardar = QAction("Guardar", self, shortcut=QKeySequence.Save, triggered=self.guardar_archivo)
        accion_guardar_como = QAction("Guardar como...", self, shortcut=QKeySequence.SaveAs, triggered=self.guardar_archivo_como)
        accion_salir = QAction("Salir", self, shortcut="Ctrl+Q", triggered=self.close)

        # --- Menú ---
        menu_archivo = self.menuBar().addMenu("&Archivo")
        menu_archivo.addAction(accion_nuevo); menu_archivo.addAction(accion_abrir)
        menu_archivo.addSeparator(); menu_archivo.addAction(accion_guardar); menu_archivo.addAction(accion_guardar_como)
        menu_archivo.addSeparator(); menu_archivo.addAction(accion_salir)

        # --- Menú Editar (acciones nativas de QTextEdit) ---
        menu_editar = self.menuBar().addMenu("&Editar")
        menu_editar.addAction(self.editor.createStandardContextMenu().actions()[0]) # Deshacer
        menu_editar.addAction(self.editor.createStandardContextMenu().actions()[1]) # Rehacer
        menu_editar.addSeparator()
        menu_editar.addAction(self.editor.createStandardContextMenu().actions()[3]) # Cortar
        menu_editar.addAction(self.editor.createStandardContextMenu().actions()[4]) # Copiar
        menu_editar.addAction(self.editor.createStandardContextMenu().actions()[5]) # Pegar

        self.actualizar_titulo()
        self.actualizar_estado()

    def actualizar_titulo(self):
        nombre = os.path.basename(self.ruta_archivo_actual) if self.ruta_archivo_actual else "Sin Título"
        self.setWindowTitle(f"{nombre}[*] - Editor de Texto Nemás OS")

    def actualizar_estado(self):
        cursor = self.editor.textCursor()
        linea = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.statusBar().showMessage(f"Línea: {linea}, Columna: {col}")

    def nuevo_archivo(self):
        if not self.confirmar_cambios(): return
        self.editor.clear()
        self.ruta_archivo_actual = None
        self.setWindowModified(False)
        self.actualizar_titulo()

    def abrir_archivo(self):
        if not self.confirmar_cambios(): return
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Archivos de Texto (*.txt);;Todos los archivos (*)")
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    self.editor.setText(f.read())
                self.ruta_archivo_actual = ruta
                self.setWindowModified(False)
                self.actualizar_titulo()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{e}")

    def guardar_archivo(self):
        if self.ruta_archivo_actual is None:
            return self.guardar_archivo_como()
        else:
            try:
                with open(self.ruta_archivo_actual, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.setWindowModified(False)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")
                return False

    def guardar_archivo_como(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo Como", "", "Archivos de Texto (*.txt);;Todos los archivos (*)")
        if ruta:
            self.ruta_archivo_actual = ruta
            return self.guardar_archivo()
        return False

    def confirmar_cambios(self):
        if not self.isWindowModified():
            return True

        respuesta = QMessageBox.question(self, "Cambios no guardados",
            "Tienes cambios sin guardar. ¿Quieres guardarlos?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save)

        if respuesta == QMessageBox.Save:
            return self.guardar_archivo()
        elif respuesta == QMessageBox.Cancel:
            return False
        return True # Para Discard

    def closeEvent(self, event):
        if self.confirmar_cambios():
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = EditorTextoGUI()
    ventana.show()
    sys.exit(app.exec_())
