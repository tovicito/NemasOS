#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# generador_informe_gui.py - GUI para analizar el contenido de un directorio (Nemás OS)
#

import sys
import os
from collections import Counter
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView, QMessageBox, QGroupBox, QSplitter
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QPainter, QColor

class ReportWorker(QThread):
    """ Hilo para analizar un directorio en segundo plano. """
    report_finalizado = pyqtSignal(dict)

    def __init__(self, directorio):
        super().__init__()
        self.directorio = directorio
        self.activo = True

    def run(self):
        report = {'total_size': 0, 'total_files': 0, 'total_dirs': 0, 'ext_counts': Counter(), 'ext_sizes': Counter(), 'error': None}
        try:
            for dirpath, dirnames, filenames in os.walk(self.directorio):
                if not self.activo: break
                report['total_dirs'] += len(dirnames)
                for f in filenames:
                    if not self.activo: break
                    fp = os.path.join(dirpath, f)
                    try:
                        if os.path.islink(fp): continue
                        size = os.path.getsize(fp)
                        report['total_files'] += 1
                        report['total_size'] += size
                        ext = os.path.splitext(f)[1].lower() if '.' in f else '.sin_ext'
                        report['ext_counts'][ext] += 1
                        report['ext_sizes'][ext] += size
                    except FileNotFoundError:
                        continue
            if not self.activo: report['error'] = "Cancelado por el usuario."
        except Exception as e:
            report['error'] = str(e)
        self.report_finalizado.emit(report)

    def stop(self):
        self.activo = False

class ReportGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Generador de Informes de Archivos de Nemás OS')
        self.setGeometry(150, 150, 900, 700)
        layout = QVBoxLayout(self)

        # --- Selección y Acción ---
        top_layout = QHBoxLayout()
        self.linea_directorio = QLineEdit(); self.linea_directorio.setPlaceholderText("Selecciona un directorio...")
        btn_sel = QPushButton("Seleccionar..."); btn_sel.clicked.connect(self.seleccionar_directorio)
        self.btn_gen = QPushButton("Generar Informe"); self.btn_gen.clicked.connect(self.generar_informe)
        top_layout.addWidget(self.linea_directorio, 1); top_layout.addWidget(btn_sel); top_layout.addWidget(self.btn_gen)
        layout.addLayout(top_layout)

        # --- Resumen ---
        summary_box = QGroupBox("Resumen General")
        summary_layout = QHBoxLayout(summary_box)
        self.label_files = QLabel("Archivos: 0"); self.label_dirs = QLabel("Directorios: 0"); self.label_size = QLabel("Tamaño Total: 0 B")
        summary_layout.addWidget(self.label_files); summary_layout.addWidget(self.label_dirs); summary_layout.addWidget(self.label_size)
        layout.addWidget(summary_box)

        # --- Divisor para Tabla y Gráfico ---
        splitter = QSplitter(Qt.Horizontal)

        # --- Tabla de Desglose ---
        self.tabla_desglose = QTableWidget(); self.tabla_desglose.setColumnCount(3)
        self.tabla_desglose.setHorizontalHeaderLabels(["Extensión", "Nº Archivos", "Tamaño Total"])
        self.tabla_desglose.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_desglose.setSortingEnabled(True)
        splitter.addWidget(self.tabla_desglose)

        # --- Gráfico de Tarta ---
        self.chart_view = QChartView(); self.chart_view.setRenderHint(QPainter.Antialiasing)
        chart = QChart(); chart.setTitle("Distribución por Tamaño")
        self.chart_view.setChart(chart)
        splitter.addWidget(self.chart_view)

        splitter.setSizes([400, 500])
        layout.addWidget(splitter, 1)

        self.label_estado = QLabel("Listo."); layout.addWidget(self.label_estado)

    def seleccionar_directorio(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio", os.path.expanduser("~"))
        if directorio: self.linea_directorio.setText(directorio)

    def generar_informe(self):
        directorio = self.linea_directorio.text()
        if not directorio:
            QMessageBox.warning(self, "Falta Directorio", "Por favor, selecciona un directorio."); return

        if self.worker and self.worker.isRunning(): self.worker.stop()

        self.label_estado.setText(f"Analizando '{directorio}'..."); self.btn_gen.setEnabled(False)
        self.worker = ReportWorker(directorio); self.worker.report_finalizado.connect(self.mostrar_informe)
        self.worker.start()

    def mostrar_informe(self, report):
        self.btn_gen.setEnabled(True)
        if report['error']:
            self.label_estado.setText(f"Error: {report['error']}"); return

        # --- Poblar Resumen ---
        self.label_files.setText(f"Archivos: {report['total_files']:,}")
        self.label_dirs.setText(f"Directorios: {report['total_dirs']:,}")
        self.label_size.setText(f"Tamaño Total: {self.format_size(report['total_size'])}")

        # --- Poblar Tabla ---
        self.tabla_desglose.setRowCount(0); self.tabla_desglose.setSortingEnabled(False)
        sorted_exts = sorted(report['ext_sizes'].items(), key=lambda item: item[1], reverse=True)
        for ext, size in sorted_exts:
            row = self.tabla_desglose.rowCount(); self.tabla_desglose.insertRow(row)
            count = report['ext_counts'][ext]
            self.tabla_desglose.setItem(row, 0, QTableWidgetItem(ext))
            self.tabla_desglose.setItem(row, 1, self.create_numeric_item(count))
            self.tabla_desglose.setItem(row, 2, self.create_numeric_item(size, self.format_size(size)))
        self.tabla_desglose.setSortingEnabled(True)

        # --- Poblar Gráfico ---
        series = QPieSeries(); series.setHoleSize(0.35)
        otros_size = 0; total_size = report['total_size']
        for i, (ext, size) in enumerate(sorted_exts):
            if i < 10: # Mostrar top 10 en el gráfico
                slice = series.append(f"{ext} ({self.format_size(size)})", size)
                slice.setLabelVisible(); slice.setLabelColor(QColor('white'))
            else:
                otros_size += size
        if otros_size > 0: series.append(f"Otros ({self.format_size(otros_size)})", otros_size)

        chart = self.chart_view.chart()
        chart.removeAllSeries(); chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignRight)

        self.label_estado.setText("Informe generado con éxito.")

    def format_size(self, size_bytes):
        if size_bytes == 0: return "0 B"
        units = ("B", "KB", "MB", "GB", "TB"); i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024; i += 1
        return f"{size_bytes:.2f} {units[i]}"

    def create_numeric_item(self, value, text=None):
        item = QTableWidgetItem(text or str(value))
        item.setData(Qt.UserRole, value)
        return item

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning(): self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setStyle('Fusion')
    ventana = ReportGUI(); ventana.show()
    sys.exit(app.exec_())
