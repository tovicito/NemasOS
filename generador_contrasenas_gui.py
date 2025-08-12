#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# generador_contrasenas_gui.py - Una utilidad con GUI para generar contraseñas seguras (Nemás OS)
#

import sys
import random
import string
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QSpinBox, QLineEdit, QLabel,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class GeneradorContrasenasGUI(QWidget):
    """
    Clase principal para la aplicación de generación de contraseñas.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Inicializa la interfaz de usuario, creando y organizando todos los widgets.
        """
        self.setWindowTitle('Generador de Contraseñas de Nemás OS')
        self.setGeometry(300, 300, 450, 300)

        # --- Layouts ---
        layout_principal = QVBoxLayout()
        layout_opciones = QVBoxLayout()
        layout_longitud = QHBoxLayout()
        layout_resultado = QHBoxLayout()

        # --- Título ---
        label_titulo = QLabel('Configura tu Contraseña Segura')
        label_titulo.setAlignment(Qt.AlignCenter)
        font_titulo = QFont()
        font_titulo.setPointSize(16)
        font_titulo.setBold(True)
        label_titulo.setFont(font_titulo)
        layout_principal.addWidget(label_titulo)

        # --- Opciones de Longitud ---
        label_longitud = QLabel('Longitud de la contraseña:')
        self.spin_longitud = QSpinBox()
        self.spin_longitud.setRange(8, 128)
        self.spin_longitud.setValue(16)
        self.spin_longitud.setToolTip("Elige una longitud entre 8 y 128 caracteres.")
        layout_longitud.addWidget(label_longitud)
        layout_longitud.addWidget(self.spin_longitud)
        layout_opciones.addLayout(layout_longitud)

        # --- Opciones de Caracteres ---
        self.check_mayusculas = QCheckBox('Incluir Mayúsculas (A-Z)')
        self.check_mayusculas.setChecked(True)
        self.check_minusculas = QCheckBox('Incluir Minúsculas (a-z)')
        self.check_minusculas.setChecked(True)
        self.check_numeros = QCheckBox('Incluir Números (0-9)')
        self.check_numeros.setChecked(True)
        self.check_simbolos = QCheckBox('Incluir Símbolos (!@#$%)')
        self.check_simbolos.setChecked(True)

        layout_opciones.addWidget(self.check_mayusculas)
        layout_opciones.addWidget(self.check_minusculas)
        layout_opciones.addWidget(self.check_numeros)
        layout_opciones.addWidget(self.check_simbolos)

        layout_principal.addLayout(layout_opciones)
        layout_principal.addStretch(1) # Espaciador

        # --- Botón de Generar ---
        btn_generar = QPushButton('Generar Contraseña')
        btn_generar.setStyleSheet("padding: 10px; font-size: 14px;")
        btn_generar.clicked.connect(self.generar_contrasena)
        layout_principal.addWidget(btn_generar)

        # --- Resultado y Botón de Copiar ---
        self.line_resultado = QLineEdit()
        self.line_resultado.setReadOnly(True)
        self.line_resultado.setPlaceholderText('Aquí aparecerá tu contraseña segura...')
        self.line_resultado.setStyleSheet("padding: 5px;")

        btn_copiar = QPushButton('Copiar')
        btn_copiar.setToolTip("Copia la contraseña generada al portapapeles.")
        btn_copiar.clicked.connect(self.copiar_al_portapapeles)

        layout_resultado.addWidget(self.line_resultado)
        layout_resultado.addWidget(btn_copiar)
        layout_principal.addLayout(layout_resultado)

        self.setLayout(layout_principal)

    def generar_contrasena(self):
        """
        Genera una contraseña basándose en las opciones seleccionadas por el usuario.
        """
        longitud = self.spin_longitud.value()

        opciones = {
            'mayusculas': (self.check_mayusculas.isChecked(), string.ascii_uppercase),
            'minusculas': (self.check_minusculas.isChecked(), string.ascii_lowercase),
            'numeros': (self.check_numeros.isChecked(), string.digits),
            'simbolos': (self.check_simbolos.isChecked(), string.punctuation)
        }

        caracteres_disponibles = "".join([charset for flag, charset in opciones.values() if flag])

        if not caracteres_disponibles:
            QMessageBox.warning(self, 'Error de Selección', 'Debes seleccionar al menos un tipo de caracter para generar la contraseña.')
            return

        contrasena_generada = []
        # Asegurar que cada tipo de caracter seleccionado esté presente
        for flag, charset in opciones.values():
            if flag:
                contrasena_generada.append(random.choice(charset))

        # Rellenar el resto de la contraseña con caracteres aleatorios de todos los disponibles
        longitud_restante = longitud - len(contrasena_generada)
        if longitud_restante > 0:
            contrasena_generada.extend(random.choices(caracteres_disponibles, k=longitud_restante))

        # Mezclar la lista para que los caracteres garantizados no estén siempre al principio
        random.shuffle(contrasena_generada)

        self.line_resultado.setText("".join(contrasena_generada))

    def copiar_al_portapapeles(self):
        """
        Copia el contenido del campo de resultado al portapapeles del sistema.
        """
        contrasena = self.line_resultado.text()
        if contrasena:
            clipboard = QApplication.clipboard()
            clipboard.setText(contrasena)
            QMessageBox.information(self, 'Copiado', '¡Contraseña copiada al portapapeles!')
        else:
            QMessageBox.warning(self, 'Aviso', 'No hay ninguna contraseña que copiar. Por favor, genera una primero.')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # El estilo 'Fusion' proporciona un look moderno y consistente en diferentes plataformas
    app.setStyle('Fusion')

    ventana = GeneradorContrasenasGUI()
    ventana.show()
    sys.exit(app.exec_())
