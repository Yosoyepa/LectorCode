"""
Ventana principal para procesar y renombrar imágenes escaneadas de guías de envío.
"""
import os
import sys
from typing import Dict, List, Optional

# PyQt imports
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QMessageBox, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap

# Core imports
try:
    from src.core import processing_handler
except ImportError as e:
    error_msg = f"Error Crítico: No se pudieron importar los módulos core: {e}"
    print(error_msg)
    sys.exit(error_msg)

# Local imports
try:
    from . import resources_rc
    print("Archivo de recursos 'resources_rc.py' importado correctamente.")
except ImportError:
    print("ADVERTENCIA: No se encontró 'resources_rc.py'. "
          "Asegúrate de haber compilado 'iconos.qrc'. "
          "Los iconos definidos en el .ui pueden no cargarse.")

# Imports de componentes y utilidades
from src.ui.components.image_preview import ImagePreviewComponent
from src.ui.components.item_processor import ItemProcessor
from src.ui.controllers.item_list_controller import ItemListController 
from src.ui.controllers.processing_controller import ProcessingController
from src.utils.ui_helpers import configure_tooltips, set_widgets_enabled, clear_preview_widgets
from src.utils.message_helpers import show_error_message, show_warning_message, show_info_message, confirm_action, create_processing_summary
from src.utils.file_helpers import get_image_files_dialog, is_valid_filename

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

        # Inicializar controladores y componentes
        self._inicializar_componentes()
        self._conectar_eventos()
        self._inicializar_estado_ui()

    # =====================================
    # ===== INICIALIZACIÓN Y CONFIGURACIÓN =====
    # =====================================

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
        self.label_nombre_archivo = self.findChild(QLabel, "label_nombre_archivo")
        
        # Widgets de interacción
        self.lista_imagenes = self.findChild(QtWidgets.QListWidget, "lista_imagenes")
        self.linea_edicion_texto = self.findChild(QLineEdit, "linea_edicion_texto")
        self.boton_guardar = self.findChild(QPushButton, "boton_guardar")
        
        # Diagnóstico para el botón guardar
        if not self.boton_guardar:
            print("ADVERTENCIA: No se pudo encontrar el botón 'boton_guardar' en la UI")
        else:
            print("Botón guardar encontrado correctamente")
        
        self.boton_volver_imagen = self.findChild(QPushButton, "boton_volver_imagen")
        self.boton_siguiente_imagen = self.findChild(QPushButton, "boton_siguiente_imagen")
        self.boton_cargar = self.findChild(QPushButton, "boton_cargar")
        self.boton_procesar = self.findChild(QPushButton, "boton_procesar")
        self.boton_seleccionar_todo = self.findChild(QPushButton, "boton_seleccionar_todo") 
        self.boton_deseleccionar = self.findChild(QPushButton, "boton_deseleccionar")

        # Verificar widgets críticos
        self._verificar_widgets_criticos()

    def _verificar_widgets_criticos(self) -> None:
        """Verifica que todos los widgets críticos se hayan encontrado."""
        widgets_criticos = {
            "lista_imagenes": getattr(self, 'lista_imagenes', None),
            "label_preview": self.label_preview,
            "linea_edicion_texto": self.linea_edicion_texto,
            "boton_guardar": self.boton_guardar,
            "boton_volver_imagen": self.boton_volver_imagen,
            "boton_siguiente_imagen": self.boton_siguiente_imagen
        }
        
        for nombre, widget in widgets_criticos.items():
            if not widget:
                print(f"Advertencia: Widget '{nombre}' no encontrado.")

    def _inicializar_componentes(self) -> None:
        """Inicializa los controladores y componentes de la aplicación."""
        # Controladores
        self.item_list_controller = ItemListController(self.lista_imagenes)
        self.processing_controller = ProcessingController(self)
        
        # Componentes
        self.image_preview = ImagePreviewComponent(self.label_preview, self.label_nombre_archivo)
        
        # Instalar filtro de eventos en la lista
        if hasattr(self, 'lista_imagenes'):
            self.lista_imagenes.installEventFilter(self)

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
        if hasattr(self, 'item_list_controller'):
            self.item_list_controller.connect_item_clicked(self._item_seleccionado_cambiado)
            self.item_list_controller.connect_current_item_changed(self._item_seleccionado_cambiado)
            self.item_list_controller.connect_item_changed(self.actualizar_estado_ui)
        else:
            print("Error Crítico: No se pudo inicializar el controlador de lista de imágenes.")

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
        widgets_a_deshabilitar = [
            'boton_procesar', 'linea_edicion_texto', 'boton_guardar', 
            'boton_volver_imagen', 'boton_siguiente_imagen'
        ]
        set_widgets_enabled(self, widgets_a_deshabilitar, False)

    def _limpiar_widgets_visualizacion(self) -> None:
        """Limpia los widgets de visualización."""
        clear_preview_widgets(self.label_preview, self.linea_edicion_texto)

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
        configure_tooltips(self, tooltips)

    # ====================================
    # ===== GESTIÓN DE ESTADO DE UI =====
    # ====================================

    def actualizar_estado_ui(self, *args) -> None:
        """Actualiza el estado habilitado de botones según la selección y edición."""
        if not hasattr(self, 'lista_imagenes'): 
            return

        items_chequeados = self.item_list_controller.get_checked_items()
        item_actual = self.item_list_controller.get_current_item()
        num_chequeados = len(items_chequeados)
        num_total_items = self.item_list_controller.get_item_count()
        fila_actual = self.item_list_controller.get_current_row()

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
        set_widgets_enabled(self, widgets_a_controlar, habilitado)

        # Al re-habilitar, ajustar el estado específico
        if habilitado:
            self.actualizar_estado_ui()

    # ======================================
    # ===== FUNCIONES PRINCIPALES DE UI =====
    # ======================================

    def cargar_imagenes(self) -> None:
        """Abre un diálogo para seleccionar imágenes y las carga en la lista."""
        if not hasattr(self, 'lista_imagenes'):
            show_error_message(self, "Error", "El componente lista de imágenes no está disponible.")
            return
            
        archivos = get_image_files_dialog(self)
        if not archivos: 
            return

        # Limpiar y cargar nuevos archivos
        self.item_list_controller.clear_list()
        self._limpiar_widgets_visualizacion()
        archivos_cargados_count = self.item_list_controller.load_files(archivos)
        
        print(f"Se cargaron {archivos_cargados_count} archivos.")
        
        # Seleccionar el primer item automáticamente
        self.item_list_controller.select_first_item()
        self.actualizar_estado_ui()

    def _item_seleccionado_cambiado(self, item_actual, item_previo=None) -> None:
        """Actualiza UI cuando el item actual cambia (clic o teclado)."""
        item_a_mostrar = None
        if isinstance(item_actual, QListWidgetItem):
            item_a_mostrar = item_actual

        print(f"Item seleccionado cambiado a: {item_a_mostrar.text() if item_a_mostrar else 'None'}")

        # Actualizar previsualización y edición
        self.image_preview.show_preview(item_a_mostrar)
        self.preparar_edicion_manual(item_a_mostrar)
        self.actualizar_estado_ui()

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
        item_actual = self.item_list_controller.get_current_item()
        if not item_actual:
            show_warning_message(self, "Guardar Manual", 
                               "Por favor, selecciona un archivo de la lista para renombrar.")
            return

        nuevo_nombre_base = self.linea_edicion_texto.text().strip()
        
        # Validar el nuevo nombre
        valido, mensaje = is_valid_filename(nuevo_nombre_base)
        if not valido:
            show_warning_message(self, "Nombre Inválido", mensaje)
            return
            
        # Procesar el renombrado
        resultado = ItemProcessor.rename_item_manual(item_actual, nuevo_nombre_base)
        self._procesar_resultado_renombrado(item_actual, resultado)

    def _procesar_resultado_renombrado(self, item: QListWidgetItem, resultado: dict) -> None:
        """Procesa el resultado de un intento de renombrado manual."""
        status = resultado.get("status", "")
        
        if status == "success":
            # Renombrado exitoso - Pedir confirmación
            nuevo_nombre = resultado["new_name"]
            nueva_ruta = resultado["new_path"]
            
            # Usar QMessageBox.No como botón por defecto en lugar de QMessageBox.Cancel
            if confirm_action(self, 'Confirmar Renombrado Manual',
                             f"¿Renombrar '{item.text()}' a '{nuevo_nombre}'?",
                             QMessageBox.No):
                # Actualizar item
                ItemProcessor.update_renamed_item(item, nuevo_nombre, nueva_ruta)
                show_info_message(self, "Éxito", f"Archivo renombrado a:\n'{nuevo_nombre}'")
                
        elif status == "no_rename_needed":
            # No necesita renombrarse
            show_info_message(self, "Sin Cambios", 
                            resultado.get("message", "El nombre editado es el mismo que el actual."))
            
        elif status == "target_exists":
            # Conflicto con archivo existente
            show_warning_message(self, "Conflicto de Nombre", 
                                resultado.get("message", "Ya existe un archivo con ese nombre."))
            
        else:  # "error", "rename_failed" u otros estados
            # Error en el renombrado
            show_error_message(self, "Error al Renombrar", 
                             resultado.get("message", "No se pudo renombrar el archivo."))
            
        # Actualizar estado UI después de cualquier operación
        self.actualizar_estado_ui()

    def seleccionar_todo(self) -> None:
        """Marca todos los items de la lista."""
        self.item_list_controller.select_all()
        self.actualizar_estado_ui()

    def deseleccionar_todo(self) -> None:
        """Desmarca todos los items de la lista."""
        self.item_list_controller.deselect_all()
        self.actualizar_estado_ui()

    def _navegar_imagen_anterior(self) -> None:
        """Selecciona el item anterior en la lista."""
        self.item_list_controller.navigate_previous()

    def _navegar_siguiente_imagen(self) -> None:
        """Selecciona el item siguiente en la lista."""
        self.item_list_controller.navigate_next()

    def procesar_seleccionados(self) -> None:
        """Procesa todos los items seleccionados con checkmark."""
        items_a_procesar = self.item_list_controller.get_checked_items()
        
        if not items_a_procesar:
            show_warning_message(self, "Sin Selección", 
                               "Por favor, selecciona (marca) al menos un archivo para procesar.")
            return

        # Procesar los items
        resultados = self.processing_controller.process_items(
            items_a_procesar, 
            self._set_controles_habilitados
        )
        
        # Mostrar resumen
        create_processing_summary(self, resultados, len(items_a_procesar))

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
        if confirm_action(self, 'Confirmar Salida', 
                         "¿Estás seguro de que quieres salir?", 
                         QMessageBox.No):
            print("Cerrando la aplicación...")
            event.accept()
        else:
            print("Cierre cancelado.")
            event.ignore()