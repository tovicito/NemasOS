#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# calculadora_gui.py - Una calculadora con GUI (Nemás OS)
#

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt

class CalculadoraGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.expresion = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculadora de Nemás OS')
        self.setGeometry(400, 400, 350, 450)
        layout = QVBoxLayout(self)

        # --- Display ---
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        font = self.display.font(); font.setPointSize(28); self.display.setFont(font)
        self.display.setFixedHeight(60)
        layout.addWidget(self.display)

        # --- Botones ---
        grid = QGridLayout()
        botones = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
            ('C', 0, 0), ('⌫', 0, 1), ('(', 0, 2), (')', 0, 3)
        ]

        for texto, fila, col in botones:
            boton = QPushButton(texto)
            boton.setFixedSize(70, 50)
            font = boton.font(); font.setPointSize(16); boton.setFont(font)
            boton.clicked.connect(self.on_click)
            grid.addWidget(boton, fila, col)

        layout.addLayout(grid)

    def on_click(self):
        boton = self.sender()
        texto_boton = boton.text()

        if texto_boton == '=':
            self.calcular_resultado()
        elif texto_boton == 'C':
            self.expresion = ""
        elif texto_boton == '⌫':
            self.expresion = self.expresion[:-1]
        else:
            self.expresion += texto_boton

        self.actualizar_display()

    def calcular_resultado(self):
        try:
            # Sanitize the expression to only allow safe characters
            safe_chars = "0123456789.+-*/() "
            if any(char not in safe_chars for char in self.expresion):
                raise ValueError("Caracter no permitido en la expresión")

            # Eval is safe here because we've controlled the input string
            resultado = eval(self.expresion)
            self.expresion = str(resultado)
        except Exception:
            self.expresion = "Error"

    def actualizar_display(self):
        self.display.setText(self.expresion)

    def keyPressEvent(self, event):
        """Maneja la entrada del teclado."""
        key = event.key()
        text = event.text()

        if Qt.Key_0 <= key <= Qt.Key_9 or text in '.+-*/()':
            self.expresion += text
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            self.calcular_resultado()
        elif key == Qt.Key_Backspace:
            self.expresion = self.expresion[:-1]
        elif key == Qt.Key_Escape:
            self.expresion = ""

        self.actualizar_display()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = CalculadoraGUI()
    ventana.show()
    sys.exit(app.exec_())
