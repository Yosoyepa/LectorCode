"""
Ventana principal para procesar y renombrar imágenes escaneadas de guías de envío.
"""
import os
import sys
import re
from typing import Dict, List, Optional, Tuple, Union

# PyQt imports - organizados por componentes
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QListWidgetItem, QMessageBox, 
    QLabel, QTextEdit, QProgressDialog, QPushButton, QLineEdit
)
from PyQt5.QtCore import QDir, Qt, QEvent
from PyQt5.QtGui import QPixmap, QColor

# Core imports
try:
    from src.core import file_operations
    from src.core import image_processor
except ImportError as e:
    error_msg = f"Error Crítico: No se pudieron importar los módulos core: {e}"
    print(error_msg)
    sys.exit(error_msg)

# Resources import
try:
    from . import resources_rc
    print("Archivo de recursos 'resources_rc.py' importado correctamente.")
except ImportError:
    print("ADVERTENCIA: No se encontró 'resources_rc.py'. "
          "Asegúrate de haber compilado 'iconos.qrc'. "
          "Los iconos definidos en el .ui pueden no cargarse.")

# UI path
UI_PATH = os.path.join(os.path.dirname(__file__), 'ui_files', 'Main_Window.ui')


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación para procesar y renombrar
    imágenes escaneadas de guías de envío, con navegación y edición manual.
    """

    def __init__(self):
        """Inicializa la ventana principal, carga la UI y conecta eventos."""
        super(MainWindow, self).__init__()

        # Configurar la interfaz de usuario
        self._cargar_ui()

        # Salir si la carga de UI falló
        if not hasattr(self, 'centralwidget'):
            print("Error fatal post-carga: La UI no parece haberse cargado correctamente. Saliendo.")
            sys.exit(1)

        self._conectar_eventos()
        self._inicializar_estado_ui()

        # Instalar filtro de eventos en la lista
        if hasattr(self, 'lista_imagenes'):
            self.lista_imagenes.installEventFilter(self)

    # =======================================
    # ===== INICIALIZACIÓN Y CONFIGURACIÓN =====
    # =======================================

    def _cargar_ui(self) -> None:
        """Carga la interfaz de usuario desde el archivo .ui."""
        try:
            uic.loadUi(UI_PATH, self)
            self._buscar_widgets_principales()
        except FileNotFoundError:
            mensaje = f"No se pudo encontrar el archivo UI en {UI_PATH}"
            print(f"Error Fatal: {mensaje}")
            QMessageBox.critical(None, "Error de Inicialización", mensaje)
            sys.exit(1)
        except Exception as e:
            mensaje = f"Error al cargar la interfaz: {str(e)}"
            print(f"Error Fatal al cargar la interfaz: {e}")
            QMessageBox.critical(None, "Error de Inicialización", mensaje)
            sys.exit(1)

    def _buscar_widgets_principales(self) -> None:
        """Busca y guarda referencias a los widgets principales de la UI."""
        # Widgets de visualización
        self.label_preview = self.findChild(QLabel, "label_preview")
        
        # Widgets de interacción
        self.linea_edicion_texto = self.findChild(QLineEdit, "linea_edicion_texto")
        self.boton_guardar = self.findChild(QPushButton, "boton_guardar")
        self.boton_volver_imagen = self.findChild(QPushButton, "boton_volver_imagen")
        self.boton_siguiente_imagen = self.findChild(QPushButton, "boton_siguiente_imagen")

        # Verificar widgets críticos
        self._verificar_widgets_criticos()

    def _verificar_widgets_criticos(self) -> None:
        """Verifica que todos los widgets críticos se hayan encontrado."""
        widgets_criticos = {
            "label_preview": self.label_preview,
            "linea_edicion_texto": self.linea_edicion_texto,
            "boton_guardar": self.boton_guardar,
            "boton_volver_imagen": self.boton_volver_imagen,
            "boton_siguiente_imagen": self.boton_siguiente_imagen
        }
        
        for nombre, widget in widgets_criticos.items():
            if not widget:
                print(f"Advertencia: Widget '{nombre}' no encontrado.")

    def _conectar_eventos(self) -> None:
        """Conecta las señales de los widgets a los métodos correspondientes."""
        self._conectar_botones_principales()
        self._conectar_lista_imagenes()
        self._conectar_edicion_navegacion()

    def _conectar_botones_principales(self) -> None:
        """Conecta los botones principales de la interfaz."""
        if hasattr(self, 'boton_cargar'): 
            self.boton_cargar.clicked.connect(self.cargar_imagenes)
        if hasattr(self, 'boton_procesar'): 
            self.boton_procesar.clicked.connect(self.procesar_seleccionados)
        if hasattr(self, 'boton_seleccionar_todo'): 
            self.boton_seleccionar_todo.clicked.connect(self.seleccionar_todo)
        if hasattr(self, 'boton_deseleccionar'): 
            self.boton_deseleccionar.clicked.connect(self.deseleccionar_todo)

    def _conectar_lista_imagenes(self) -> None:
        """Conecta eventos de la lista de imágenes."""
        if hasattr(self, 'lista_imagenes'):
            self.lista_imagenes.itemClicked.connect(self._item_seleccionado_cambiado)
            self.lista_imagenes.currentItemChanged.connect(self._item_seleccionado_cambiado)
            self.lista_imagenes.itemChanged.connect(self.actualizar_estado_ui)
        else:
            print("Error Crítico: No se encontró el widget 'lista_imagenes' en la UI.")

    def _conectar_edicion_navegacion(self) -> None:
        """Conecta eventos de edición manual y navegación."""
        if self.boton_guardar:
            self.boton_guardar.clicked.connect(self.guardar_nombre_manual)
        if self.boton_volver_imagen:
            self.boton_volver_imagen.clicked.connect(self._navegar_imagen_anterior)
        if self.boton_siguiente_imagen:
            self.boton_siguiente_imagen.clicked.connect(self._navegar_siguiente_imagen)
        if self.linea_edicion_texto:
            self.linea_edicion_texto.textChanged.connect(self.actualizar_estado_ui)

    def _inicializar_estado_ui(self) -> None:
        """Configura el estado inicial de los widgets de la interfaz."""
        self._deshabilitar_controles_iniciales()
        self._limpiar_widgets_visualizacion()
        self._configurar_tooltips()

    def _deshabilitar_controles_iniciales(self) -> None:
        """Deshabilita controles que requieren selección/carga previa."""
        if hasattr(self, 'boton_procesar'): 
            self.boton_procesar.setEnabled(False)
        if self.linea_edicion_texto: 
            self.linea_edicion_texto.setEnabled(False)
        if self.boton_guardar: 
            self.boton_guardar.setEnabled(False)
        if self.boton_volver_imagen: 
            self.boton_volver_imagen.setEnabled(False)
        if self.boton_siguiente_imagen: 
            self.boton_siguiente_imagen.setEnabled(False)

    def _limpiar_widgets_visualizacion(self) -> None:
        """Limpia los widgets de visualización."""
        if self.label_preview:
            self.label_preview.clear()
            self.label_preview.setText("Selecciona un archivo para previsualizar.")
            self.label_preview.setAlignment(Qt.AlignCenter)
        if self.linea_edicion_texto:
            self.linea_edicion_texto.clear()

    def _configurar_tooltips(self) -> None:
        """Configura los tooltips (textos de ayuda) para los widgets."""
        tooltips = {
            'boton_cargar': "Cargar archivos de imagen escaneados",
            'boton_procesar': "Procesar los archivos seleccionados (OCR/Barcode y renombrar)",
            'linea_edicion_texto': "Editar nombre base manualmente si falla el automático",
            'boton_guardar': "Guardar el nombre editado manualmente para el archivo seleccionado",
            'boton_volver_imagen': "Ver guía anterior",
            'boton_siguiente_imagen': "Ver guía siguiente"
        }
        
        for widget_name, tooltip_text in tooltips.items():
            widget = getattr(self, widget_name, None)
            if widget:
                widget.setToolTip(tooltip_text)

    # ====================================
    # ===== GESTIÓN DE ESTADO DE UI =====
    # ====================================

    def actualizar_estado_ui(self, *args) -> None:
        """Actualiza el estado habilitado de botones según la selección y edición."""
        if not hasattr(self, 'lista_imagenes'): 
            return

        items_chequeados = self.obtener_items_seleccionados()
        item_actual = self.lista_imagenes.currentItem()
        num_chequeados = len(items_chequeados)
        num_total_items = self.lista_imagenes.count()
        fila_actual = self.lista_imagenes.currentRow() if item_actual else -1

        self._actualizar_estado_botones_procesamiento(num_chequeados)
        self._actualizar_estado_edicion_manual(item_actual)
        self._actualizar_estado_navegacion(fila_actual, num_total_items)

    def _actualizar_estado_botones_procesamiento(self, num_chequeados: int) -> None:
        """Actualiza el estado de los botones de procesamiento."""
        if hasattr(self, 'boton_procesar'):
            self.boton_procesar.setEnabled(num_chequeados > 0)

    def _actualizar_estado_edicion_manual(self, item_actual: Optional[QListWidgetItem]) -> None:
        """Actualiza el estado de los controles de edición manual."""
        habilitar_edicion = (item_actual is not None)
        
        if self.linea_edicion_texto:
            self.linea_edicion_texto.setEnabled(habilitar_edicion)
            if not habilitar_edicion:
                self.linea_edicion_texto.clear()

        if self.boton_guardar:
            puede_guardar = habilitar_edicion and bool(self.linea_edicion_texto.text().strip())
            self.boton_guardar.setEnabled(puede_guardar)

    def _actualizar_estado_navegacion(self, fila_actual: int, num_total_items: int) -> None:
        """Actualiza el estado de los botones de navegación."""
        if self.boton_volver_imagen:
            self.boton_volver_imagen.setEnabled(fila_actual > 0)
        
        if self.boton_siguiente_imagen:
            self.boton_siguiente_imagen.setEnabled(
                fila_actual >= 0 and fila_actual < num_total_items - 1
            )

    def _set_controles_habilitados(self, habilitado: bool) -> None:
        """Habilita/deshabilita controles durante operaciones largas."""
        widgets_a_controlar = [
            'boton_cargar', 'boton_seleccionar_todo', 'boton_deseleccionar',
            'lista_imagenes', 'boton_procesar', 'linea_edicion_texto',
            'boton_guardar', 'boton_volver_imagen', 'boton_siguiente_imagen'
        ]
        
        for nombre_widget in widgets_a_controlar:
            if hasattr(self, nombre_widget):
                widget = getattr(self, nombre_widget)
                widget.setEnabled(habilitado)

        # Al re-habilitar, ajustar el estado específico
        if habilitado:
            self.actualizar_estado_ui()

    # ===========================================
    # ===== CARGA Y GESTIÓN DE IMÁGENES =====
    # ===========================================

    def cargar_imagenes(self) -> None:
        """Abre un diálogo para seleccionar imágenes y las carga en la lista."""
        if not hasattr(self, 'lista_imagenes'):
            QMessageBox.critical(self, "Error", "El componente lista de imágenes no está disponible.")
            return
            
        archivos = self._obtener_archivos_dialogo()
        if not archivos: 
            return

        self._limpiar_interfaz_para_nueva_carga()
        archivos_cargados_count = self._cargar_archivos_en_lista(archivos)
        
        print(f"Se cargaron {archivos_cargados_count} archivos.")
        
        # Seleccionar el primer item automáticamente
        if self.lista_imagenes.count() > 0:
            self.lista_imagenes.setCurrentRow(0)
        else:
            self.actualizar_estado_ui()

    def _obtener_archivos_dialogo(self) -> List[str]:
        """Muestra diálogo para seleccionar archivos y devuelve la lista de rutas."""
        directorio_inicial = QDir.homePath()
        archivos, _ = QFileDialog.getOpenFileNames(
            self, "Abrir archivos de guías escaneadas", directorio_inicial,
            "Archivos de imagen (*.jpg *.jpeg *.png *.bmp *.tif *.tiff);;Todos los archivos (*)"
        )
        return archivos

    def _limpiar_interfaz_para_nueva_carga(self) -> None:
        """Limpia la interfaz para una nueva carga de archivos."""
        self.lista_imagenes.clear()
        
        if self.label_preview:
            self.label_preview.clear()
            self.label_preview.setText("Previsualización")
            
        if self.linea_edicion_texto:
            self.linea_edicion_texto.clear()

    def _cargar_archivos_en_lista(self, archivos: List[str]) -> int:
        """Carga los archivos en la lista y devuelve el número de archivos cargados."""
        archivos_cargados_count = 0
        
        for ruta_completa in archivos:
            if os.path.exists(ruta_completa) and os.path.isfile(ruta_completa):
                self._agregar_item_a_lista(ruta_completa)
                archivos_cargados_count += 1
            else:
                print(f"Advertencia: Archivo no encontrado '{ruta_completa}', omitido.")
                
        return archivos_cargados_count

    def _agregar_item_a_lista(self, ruta_completa: str) -> None:
        """Crea un QListWidgetItem, le asocia la ruta y lo añade a la lista."""
        nombre_archivo = os.path.basename(ruta_completa)
        item = QListWidgetItem(nombre_archivo)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, ruta_completa)
        self.lista_imagenes.addItem(item)

    # ======================================
    # ===== PREVISUALIZACIÓN DE IMÁGENES =====
    # ======================================

    def _item_seleccionado_cambiado(self, item_actual, item_previo=None) -> None:
        """Actualiza UI cuando el item actual cambia (clic o teclado)."""
        item_a_mostrar = None
        if isinstance(item_actual, QListWidgetItem):
            item_a_mostrar = item_actual

        print(f"Item seleccionado cambiado a: {item_a_mostrar.text() if item_a_mostrar else 'None'}")

        self.mostrar_preview_item(item_a_mostrar)
        self.preparar_edicion_manual(item_a_mostrar)
        self.actualizar_estado_ui()

    def mostrar_preview_item(self, item: Optional[QListWidgetItem]) -> None:
        """Muestra la previsualización de la imagen del item dado."""
        if not item or not self.label_preview:
            self._mostrar_preview_vacio()
            return

        ruta_completa = item.data(Qt.UserRole)
        self._actualizar_nombre_archivo(item.text())

        if not ruta_completa or not os.path.exists(ruta_completa):
            self._mostrar_error_preview(item.text(), ruta_completa)
            return

        self._cargar_imagen_preview(ruta_completa, item.text())

    def _mostrar_preview_vacio(self) -> None:
        """Muestra un estado vacío en la previsualización."""
        if self.label_preview:
            self.label_preview.clear()
            self.label_preview.setText("Selecciona un archivo")
            self.label_preview.setAlignment(Qt.AlignCenter)
            
        if hasattr(self, 'label_nombre_archivo'):
            self.label_nombre_archivo.setText("-")

    def _actualizar_nombre_archivo(self, nombre: str) -> None:
        """Actualiza el label con el nombre del archivo."""
        if hasattr(self, 'label_nombre_archivo'):
            self.label_nombre_archivo.setText(nombre)

    def _mostrar_error_preview(self, nombre: str, ruta: Optional[str]) -> None:
        """Muestra un mensaje de error en la previsualización."""
        mensaje = f"Archivo no encontrado:\n{nombre}"
        if not ruta: 
            mensaje = "Error: Ruta no asociada."
            
        self.label_preview.setText(mensaje)
        self.label_preview.setAlignment(Qt.AlignCenter)

    def _cargar_imagen_preview(self, ruta: str, nombre: str) -> None:
        """Carga y muestra una imagen en la previsualización."""
        try:
            pixmap = QPixmap(ruta)
            if pixmap.isNull():
                self.label_preview.setText(f"Error al cargar:\n{nombre}")
                self.label_preview.setAlignment(Qt.AlignCenter)
            else:
                self._mostrar_imagen_en_preview(pixmap)
        except Exception as e:
            print(f"Excepción al cargar QPixmap para '{ruta}': {e}")
            self.label_preview.setText(f"Error al mostrar:\n{nombre}")
            self.label_preview.setAlignment(Qt.AlignCenter)

    def _mostrar_imagen_en_preview(self, pixmap: QPixmap) -> None:
        """Escala y muestra un QPixmap en el QLabel 'label_preview'."""
        if not self.label_preview: 
            return
            
        scaled_pixmap = pixmap.scaled(
            self.label_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.label_preview.setPixmap(scaled_pixmap)
        self.label_preview.setAlignment(Qt.AlignCenter)

    # =================================================
    # ===== EDICIÓN MANUAL Y NAVEGACIÓN =====
    # =================================================

    def preparar_edicion_manual(self, item: Optional[QListWidgetItem]) -> None:
        """Prepara el QLineEdit para edición manual basado en el item seleccionado."""
        if not self.linea_edicion_texto: 
            return

        if item:
            nombre_actual = item.text()
            nombre_base, _ = os.path.splitext(nombre_actual)
            self.linea_edicion_texto.setText(nombre_base)
        else:
            self.linea_edicion_texto.clear()

    def guardar_nombre_manual(self) -> None:
        """Guarda el nombre editado manualmente para el item actualmente seleccionado."""
        if not self._verificar_componentes_guardado():
            return

        item_actual = self.lista_imagenes.currentItem()
        if not item_actual:
            QMessageBox.warning(self, "Guardar Manual", 
                                "Por favor, selecciona un archivo de la lista para renombrar.")
            return

        nuevo_nombre_base = self.linea_edicion_texto.text().strip()
        
        if not self._validar_nombre_nuevo(nuevo_nombre_base):
            return
            
        if self._validar_y_realizar_renombrado(item_actual, nuevo_nombre_base):
            self.actualizar_estado_ui()

    def _verificar_componentes_guardado(self) -> bool:
        """Verifica que existan los componentes necesarios para guardar."""
        if not hasattr(self, 'lista_imagenes') or not self.linea_edicion_texto or not self.boton_guardar:
            QMessageBox.critical(self, "Error", "Componentes necesarios para guardar no encontrados.")
            return False
        return True

    def _validar_nombre_nuevo(self, nombre: str) -> bool:
        """Valida que el nombre nuevo sea adecuado."""
        if not nombre:
            QMessageBox.warning(self, "Nombre Vacío", "El nuevo nombre no puede estar vacío.")
            return False

        # Validación de caracteres inválidos
        invalid_chars_pattern = r'[\<\>\:\"\/\\\|\?\*]'
        if re.search(invalid_chars_pattern, nombre):
            QMessageBox.warning(
                self, "Nombre Inválido", 
                f"El nombre '{nombre}' contiene caracteres inválidos.\nEvita: < > : \" / \\ | ? *"
            )
            return False
            
        return True

    def _validar_y_realizar_renombrado(self, item: QListWidgetItem, nuevo_nombre_base: str) -> bool:
        """Valida y realiza el renombrado del archivo."""
        ruta_original = item.data(Qt.UserRole)
        if not ruta_original or not os.path.exists(ruta_original):
            QMessageBox.critical(
                self, "Error", 
                f"El archivo original '{item.text()}' no se encuentra o su ruta es inválida."
            )
            return False

        _, extension = os.path.splitext(item.text())
        nuevo_nombre_completo = f"{nuevo_nombre_base}{extension}"
        
        # Verificar si el nombre es igual al actual
        if nuevo_nombre_completo == item.text():
            QMessageBox.information(self, "Sin Cambios", "El nombre editado es el mismo que el actual.")
            return True

        # Generar la nueva ruta y verificar conflictos
        directorio = os.path.dirname(ruta_original)
        nueva_ruta = os.path.join(directorio, nuevo_nombre_completo)
        nueva_ruta_norm = os.path.normpath(nueva_ruta)
        
        if self._verificar_conflicto_archivo(ruta_original, nueva_ruta_norm):
            return False
            
        return self._ejecutar_renombrado(item, ruta_original, nueva_ruta, nuevo_nombre_completo)

    def _verificar_conflicto_archivo(self, ruta_original: str, nueva_ruta: str) -> bool:
        """Verifica si hay conflicto con un archivo existente."""
        if os.path.exists(nueva_ruta) and os.path.normpath(ruta_original) != nueva_ruta:
            QMessageBox.warning(
                self, "Conflicto de Nombre", 
                f"Ya existe un archivo con ese nombre en esta carpeta."
            )
            return True
        return False

    def _ejecutar_renombrado(self, item: QListWidgetItem, ruta_original: str, 
                             nueva_ruta: str, nuevo_nombre: str) -> bool:
        """Ejecuta la operación de renombrado después de confirmación."""
        # Pedir confirmación
        reply = QMessageBox.question(
            self, 'Confirmar Renombrado Manual',
            f"¿Renombrar '{item.text()}' a '{nuevo_nombre}'?",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Cancel:
            return False

        # Intentar renombrar
        print(f"Intentando renombrar manualmente: '{ruta_original}' -> '{nueva_ruta}'")
        exito, mensaje_error = file_operations.rename_scan(ruta_original, nueva_ruta)

        if exito:
            self._actualizar_item_renombrado(item, nuevo_nombre, nueva_ruta)
            QMessageBox.information(self, "Éxito", f"Archivo renombrado a:\n'{nuevo_nombre}'")
            return True
        else:
            QMessageBox.critical(
                self, "Error al Renombrar", 
                f"No se pudo renombrar el archivo.\nError: {mensaje_error}"
            )
            return False

    def _actualizar_item_renombrado(self, item: QListWidgetItem, nuevo_nombre: str, nueva_ruta: str) -> None:
        """Actualiza el item en la lista después de un renombrado exitoso."""
        item.setText(nuevo_nombre)
        item.setData(Qt.UserRole, nueva_ruta)
        item.setBackground(QColor(220, 255, 220))  # Verde muy pálido para indicar éxito
        item.setForeground(QColor('black'))

    def _navegar_imagen_anterior(self) -> None:
        """Selecciona el item anterior en la lista."""
        if not hasattr(self, 'lista_imagenes'): 
            return
            
        fila_actual = self.lista_imagenes.currentRow()
        if fila_actual > 0:
            self.lista_imagenes.setCurrentRow(fila_actual - 1)

    def _navegar_siguiente_imagen(self) -> None:
        """Selecciona el item siguiente en la lista."""
        if not hasattr(self, 'lista_imagenes'): 
            return
            
        fila_actual = self.lista_imagenes.currentRow()
        if fila_actual < self.lista_imagenes.count() - 1:
            self.lista_imagenes.setCurrentRow(fila_actual + 1)

    # ===================================
    # ===== SELECCIÓN DE ITEMS =====
    # ===================================

    def obtener_items_seleccionados(self) -> List[QListWidgetItem]:
        """Obtiene los items con checkstate marcado."""
        if not hasattr(self, 'lista_imagenes'): 
            return []
            
        seleccionados = []
        for i in range(self.lista_imagenes.count()):
            item = self.lista_imagenes.item(i)
            if item and item.checkState() == Qt.Checked:
                seleccionados.append(item)
                
        return seleccionados

    def seleccionar_todo(self) -> None:
        """Marca todos los items de la lista."""
        self._cambiar_seleccion_todos(Qt.Checked)

    def deseleccionar_todo(self) -> None:
        """Desmarca todos los items de la lista."""
        self._cambiar_seleccion_todos(Qt.Unchecked)

    def _cambiar_seleccion_todos(self, estado: Qt.CheckState) -> None:
        """Cambia el estado de selección de todos los items."""
        if not hasattr(self, 'lista_imagenes'): 
            return
            
        for i in range(self.lista_imagenes.count()):
            item = self.lista_imagenes.item(i)
            if item and (item.flags() & Qt.ItemIsEnabled):
                item.setCheckState(estado)
                
        self.actualizar_estado_ui()

    # =======================================
    # ===== PROCESAMIENTO DE IMÁGENES =====
    # =======================================

    def procesar_seleccionados(self) -> None:
        """Procesa todos los items seleccionados con checkmark."""
        items_a_procesar = self.obtener_items_seleccionados()
        
        if not items_a_procesar:
            QMessageBox.warning(
                self, "Sin Selección", 
                "Por favor, selecciona (marca) al menos un archivo para procesar."
            )
            return

        total_items = len(items_a_procesar)
        resultados = self._inicializar_resultados()
        
        self._set_controles_habilitados(False)
        progress_dialog = self._crear_dialogo_progreso(total_items)
        
        try:
            self._procesar_items_con_progreso(items_a_procesar, progress_dialog, resultados)
        except Exception as e:
            print(f"Error inesperado durante el procesamiento: {e}")
            QMessageBox.critical(
                self, "Error en Procesamiento", 
                f"Ocurrió un error inesperado: {str(e)}"
            )
            resultados["errores_detalle"].append(f"Error inesperado general: {str(e)}")
        finally:
            progress_dialog.close()
            self._set_controles_habilitados(True)
            self._mostrar_resumen_procesamiento(resultados, total_items)

    def _inicializar_resultados(self) -> Dict:
        """Inicializa el diccionario de resultados del procesamiento."""
        return {
            "exito": 0, 
            "fallo_extraccion": 0, 
            "fallo_renombrado": 0, 
            "ya_existe": 0, 
            "archivo_no_encontrado": 0, 
            "errores_detalle": []
        }

    def _crear_dialogo_progreso(self, total_items: int) -> QProgressDialog:
        """Crea y configura el diálogo de progreso."""
        progress_dialog = QProgressDialog("Procesando archivos...", "Cancelar", 0, total_items, self)
        progress_dialog.setWindowTitle("Procesando")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(500)
        progress_dialog.setValue(0)
        return progress_dialog

    def _procesar_items_con_progreso(self, items: List[QListWidgetItem], 
                                    progress_dialog: QProgressDialog, 
                                    resultados: Dict) -> None:
        """Procesa los items mostrando progreso."""
        progreso = 0
        for item in items[:]:
            progreso += 1
            progress_dialog.setValue(progreso)
            progress_dialog.setLabelText(f"Procesando {progreso}/{len(items)}: {item.text()}")
            QtWidgets.QApplication.processEvents()
            
            if progress_dialog.wasCanceled():
                resultados["errores_detalle"].insert(0, "Proceso cancelado por el usuario.")
                break
                
            resultado_item = self._procesar_item(item)
            self._actualizar_contadores_resultados(resultado_item, resultados)

    def _actualizar_contadores_resultados(self, resultado_item: Dict, resultados: Dict) -> None:
        """Actualiza los contadores de resultados según el tipo de resultado."""
        tipo_resultado = resultado_item.get("tipo", "desconocido")
        
        if tipo_resultado == "exito":              
            resultados["exito"] += 1
        elif tipo_resultado == "ya_existe":        
            resultados["ya_existe"] += 1
        elif tipo_resultado == "no_encontrado":    
            resultados["archivo_no_encontrado"] += 1
        elif tipo_resultado == "extraccion":       
            resultados["fallo_extraccion"] += 1
        elif tipo_resultado == "renombrado":       
            resultados["fallo_renombrado"] += 1
            
        if tipo_resultado != "exito":
            mensaje = resultado_item.get("mensaje", "Error desconocido")
            if mensaje: 
                resultados["errores_detalle"].append(mensaje)

    def _procesar_item(self, item: QListWidgetItem) -> Dict:
        """Procesa un item individual (OCR/Barcode y renombrado)."""
        # Restaurar apariencia
        item.setBackground(QColor('white'))
        item.setForeground(QColor('black'))
        
        # Obtener datos del item
        ruta_original = item.data(Qt.UserRole)
        nombre_actual_item = item.text()
        
        # Verificar existencia del archivo
        if not ruta_original:
            mensaje = f"{nombre_actual_item}: Error interno - Ruta no asociada."
            self._marcar_item_error(item, f"{nombre_actual_item} [Error Ruta]", QColor(255, 0, 0))
            return {"tipo": "no_encontrado", "mensaje": mensaje}
            
        if not os.path.exists(ruta_original):
            mensaje = f"{nombre_actual_item}: Archivo no encontrado en ruta '{ruta_original}'."
            self._marcar_item_error(item, f"{nombre_actual_item} [No encontrado]", QColor(255, 204, 204))
            return {"tipo": "no_encontrado", "mensaje": mensaje}
        
        # Extraer número de guía
        try:
            numero_guia = image_processor.get_guide_number(ruta_original)
        except Exception as e:
            mensaje = f"{nombre_actual_item}: Error extrayendo número - {str(e)}"
            self._marcar_item_error(item, f"{nombre_actual_item} [Error OCR/BC]", QColor(255, 153, 153))
            return {"tipo": "extraccion", "mensaje": mensaje}
            
        if not numero_guia:
            mensaje = f"{nombre_actual_item}: No se pudo extraer número de guía (OCR/Barcode)."
            self._marcar_item_error(item, f"{nombre_actual_item} [No reconocido]", QColor(255, 230, 204))
            return {"tipo": "extraccion", "mensaje": mensaje}
        
        # Limpiar número de guía
        numero_guia_str = str(numero_guia).strip()
        numero_guia_limpio = "".join(filter(str.isalnum, numero_guia_str))
        
        if not numero_guia_limpio:
            mensaje = f"{nombre_actual_item}: Número de guía inválido después de limpiar ('{numero_guia_str}')."
            self._marcar_item_error(item, f"{nombre_actual_item} [Guía inválida]", QColor(255, 230, 204))
            return {"tipo": "extraccion", "mensaje": mensaje}
        
        # Preparar renombrado
        directorio = os.path.dirname(ruta_original)
        _, extension = os.path.splitext(nombre_actual_item)
        nuevo_nombre = f"{numero_guia_limpio}{extension}"
        nueva_ruta = os.path.join(directorio, nuevo_nombre)
        
        # Verificar si ya tiene el nombre correcto
        if nuevo_nombre == nombre_actual_item:
            self._marcar_item_estado(item, f"{nombre_actual_item} [Ya correcto]", QColor(220, 220, 220))
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, nueva_ruta)
            return {"tipo": "exito", "mensaje": ""}
        
        # Verificar si el destino ya existe
        if os.path.exists(os.path.normpath(nueva_ruta)):
            mensaje = f"{nombre_actual_item}: El destino '{nuevo_nombre}' ya existe."
            self._marcar_item_error(item, f"{nombre_actual_item} [Destino existe]", QColor(255, 255, 204))
            return {"tipo": "ya_existe", "mensaje": mensaje}
        
        # Renombrar
        exito_renombrado, mensaje_error = file_operations.rename_scan(ruta_original, nueva_ruta)
        
        if exito_renombrado:
            self._marcar_item_estado(item, nuevo_nombre, QColor(204, 255, 204))
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, nueva_ruta)
            return {"tipo": "exito", "mensaje": ""}
        else:
            mensaje = f"{nombre_actual_item}: Error renombrando - {mensaje_error}"
            self._marcar_item_error(item, f"{nombre_actual_item} [Error al renombrar]", QColor(255, 153, 153))
            return {"tipo": "renombrado", "mensaje": mensaje}

    def _marcar_item_error(self, item: QListWidgetItem, texto: str, color: QColor) -> None:
        """Marca un item con un estado de error."""
        if not item: 
            return
            
        item.setText(texto)
        item.setBackground(color)
        
        # Ajustar color de texto para contraste
        if color.lightnessF() < 0.5 or (color.red() > 180 and color.green() < 100):
            item.setForeground(QColor('white'))
        else:
            item.setForeground(QColor('black'))

    def _marcar_item_estado(self, item: QListWidgetItem, texto: str, color: QColor) -> None:
        """Marca un item con un estado normal."""
        if not item: 
            return
            
        item.setText(texto)
        item.setBackground(color)
        item.setForeground(QColor('black'))

    def _mostrar_resumen_procesamiento(self, resultados: Dict, total_seleccionados: int) -> None:
        """Muestra un resumen del procesamiento realizado."""
        mensaje = f"Proceso completado para {total_seleccionados} archivos seleccionados.\n\n"
        mensaje += f"  - Éxito / Ya correctos: {resultados['exito']}\n"
        mensaje += f"  - Fallo extracción (OCR/BC): {resultados['fallo_extraccion']}\n"
        mensaje += f"  - Fallo al renombrar (Error OS): {resultados['fallo_renombrado']}\n"
        mensaje += f"  - Omitidos (Destino ya existe): {resultados['ya_existe']}\n"
        mensaje += f"  - Omitidos (Archivo no encontrado): {resultados['archivo_no_encontrado']}\n"
        
        fallos_totales = (total_seleccionados - resultados['exito'])
        
        # Crear diálogo
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Resultado del Proceso")
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Warning if fallos_totales > 0 else QMessageBox.Information)
        
        # Añadir detalles si hay errores
        if resultados["errores_detalle"]:
            self._añadir_detalles_errores(msg_box, resultados["errores_detalle"])
            
        msg_box.exec_()

    def _añadir_detalles_errores(self, msg_box: QMessageBox, errores: List[str]) -> None:
        """Añade detalles de errores al cuadro de mensaje."""
        scroll_text = QTextEdit()
        scroll_text.setReadOnly(True)
        detalles_str = "\n".join([f"- {e}" for e in errores])
        scroll_text.setText("Detalles de errores/advertencias:\n" + detalles_str)
        scroll_text.setMinimumHeight(150)
        
        try:
            msg_box.layout().addWidget(
                scroll_text, 
                msg_box.layout().rowCount(), 
                0, 
                1, 
                msg_box.layout().columnCount()
            )
            msg_box.setStyleSheet("QMessageBox { messagebox-width: 500px; }")
        except Exception as layout_e:
            print(f"Error añadiendo detalles al QMessageBox layout: {layout_e}")
            msg_box.setDetailedText("\n".join(errores))

    # ==================================
    # ===== EVENTOS DE LA VENTANA =====
    # ==================================

    def eventFilter(self, source, event) -> bool:
        """Filtro de eventos para manejo de teclas en la lista."""
        if hasattr(self, 'lista_imagenes') and source is self.lista_imagenes:
            if event.type() == QEvent.KeyPress:
                # El QListWidget maneja las teclas de navegación internamente
                pass
                
        # Comportamiento normal para eventos no manejados
        return super(MainWindow, self).eventFilter(source, event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Intercepta el evento de cierre para pedir confirmación."""
        reply = QMessageBox.question(
            self, 'Confirmar Salida',
            "¿Estás seguro de que quieres salir?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            print("Cerrando la aplicación...")
            event.accept()
        else:
            print("Cierre cancelado.")
            event.ignore()