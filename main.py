import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDir
from assets.iconos import resources

class App(QtWidgets.QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        uic.loadUi('LectorCode/views/ui_files/Main_Window.ui', self)
        self.boton_cargar.clicked.connect(self.cargar)
        self.boton_seleccionar_todo.clicked.connect(self.seleccionar_todo)
        self.boton_deseleccionar.clicked.connect(self.deseleccionar_todo)
        self.lista_imagenes_cargadas.itemClicked.connect(self.mostrar_nombre_archivo)
        self.boton_guardar.clicked.connect(self.guardar_cambios)
        self.archivos_seleccionados = []
        self.linea_edicion_texto.setEnabled(False)  # Deshabilitar el QLineEdit inicialmente

    def cargar(self):
        archivos, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Abrir archivos", "C:\\", "Archivos de imagen (*.jpg *.png)"
        )
        self.lista_imagenes_cargadas.clear()
        self.archivos_seleccionados.clear()
        for archivo in archivos:
            nombre_archivo = QDir.toNativeSeparators(archivo)
            nombre_archivo = QtCore.QFileInfo(nombre_archivo).fileName()
            item = QtWidgets.QListWidgetItem(nombre_archivo)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.lista_imagenes_cargadas.addItem(item)
            self.archivos_seleccionados.append(archivo)

    def mostrar_nombre_archivo(self, item):
        nombre_archivo = item.text()
        self.label_nombre_archivo.setText(nombre_archivo)
        # Habilitar o deshabilitar el QLineEdit en función del estado de verificación del elemento
        self.linea_edicion_texto.setEnabled(item.checkState() == QtCore.Qt.Checked)

    def guardar_cambios(self):
        nombre_nuevo = self.linea_edicion_texto.text()
        for row in range(self.lista_imagenes_cargadas.count()):
            item = self.lista_imagenes_cargadas.item(row)
            if item.checkState() == QtCore.Qt.Checked:
                archivo_seleccionado = self.archivos_seleccionados[row]
                # Realizar aquí la lógica para guardar el nombre nuevo del archivo
                print(f"Se ha guardado el nombre '{nombre_nuevo}' para el archivo '{archivo_seleccionado}'")

    def seleccionar_todo(self):
        for row in range(self.lista_imagenes_cargadas.count()):
            item = self.lista_imagenes_cargadas.item(row)
            item.setCheckState(QtCore.Qt.Checked)
        self.linea_edicion_texto.setEnabled(True)  # Habilitar el QLineEdit al seleccionar todo

    def deseleccionar_todo(self):
        for row in range(self.lista_imagenes_cargadas.count()):
            item = self.lista_imagenes_cargadas.item(row)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.linea_edicion_texto.setEnabled(False) # Deshabilitar el QLineEdit al deseleccionar todo

if __name__ == "__main__":
    application = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(application.exec_())