#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# gestor_portapapeles_gui.py - Un gestor de historial del portapapeles (Nemás OS)
#

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QCheckBox, QLabel
)
from PyQt5.QtCore import Qt

class GestorPortapapelesGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        self.historial = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gestor del Portapapeles de Nemás OS')
        self.setGeometry(500, 500, 400, 500)
        layout = QVBoxLayout(self)

        # --- Controles ---
        controles_layout = QHBoxLayout()
        self.check_monitor = QCheckBox("Monitorizar Portapapeles")
        self.check_monitor.setChecked(True)
        self.check_monitor.stateChanged.connect(self.actualizar_estado)

        btn_limpiar = QPushButton("Limpiar Historial")
        btn_limpiar.clicked.connect(self.limpiar_historial)

        controles_layout.addWidget(self.check_monitor)
        controles_layout.addStretch(1)
        controles_layout.addWidget(btn_limpiar)
        layout.addLayout(controles_layout)

        # --- Lista de Historial ---
        self.lista_historial = QListWidget()
        self.lista_historial.itemDoubleClicked.connect(self.on_item_clicked)
        layout.addWidget(self.lista_historial)

        # --- Barra de Estado ---
        self.label_estado = QLabel("Monitorizando...")
        layout.addWidget(self.label_estado)

    def on_clipboard_change(self):
        if not self.check_monitor.isChecked():
            return

        texto = self.clipboard.text()

        # Evitar añadir duplicados consecutivos o texto vacío
        if texto and (not self.historial or texto != self.historial[0]):
            self.historial.insert(0, texto)
            self.lista_historial.insertItem(0, texto)

            # Limitar el historial a un tamaño razonable
            if len(self.historial) > 100:
                self.historial.pop()
                self.lista_historial.takeItem(self.lista_historial.count() - 1)

    def on_item_clicked(self, item):
        texto_seleccionado = item.text()
        # Desactivar temporalmente el monitoreo para no registrar nuestra propia acción
        monitoring_state = self.check_monitor.isChecked()
        self.check_monitor.setChecked(False)

        self.clipboard.setText(texto_seleccionado)

        self.check_monitor.setChecked(monitoring_state)
        self.label_estado.setText(f"'{texto_seleccionado[:20]}...' copiado al portapapeles.")

    def limpiar_historial(self):
        self.historial.clear()
        self.lista_historial.clear()

    def actualizar_estado(self):
        if self.check_monitor.isChecked():
            self.label_estado.setText("Monitorizando...")
        else:
            self.label_estado.setText("En pausa. El historial no se actualizará.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # Para que la ventana no se cierre al perder el foco y siga funcionando
    # en segundo plano, no la hacemos hija de ninguna otra ventana.
    # También se podría implementar como un ícono en la bandeja del sistema.
    ventana = GestorPortapapelesGUI()
    ventana.show()
    sys.exit(app.exec_())
