# src/ui/main_window.py
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
# Importar clases específicas y Qt directamente para UserRole
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QListWidgetItem,
                             QMessageBox, QLabel, QTextEdit, QProgressDialog)
from PyQt5.QtCore import QDir, Qt # Qt contiene UserRole y constantes de alineación/escalado
from PyQt5.QtGui import QPixmap

# Importaciones de módulos core
try:
    # Asume que main_window.py está en src/ui/ y los módulos core en src/core/
    from src.core import file_operations
    from src.core import image_processor
except ImportError as e:
     # Error crítico si no se pueden importar los módulos core
     print(f"Error Crítico: No se pudieron importar los módulos core: {e}")
     # Salir si las importaciones fallan, ya que la app no puede funcionar
     sys.exit(f"Error Crítico: No se pudieron importar los módulos core: {e}")

# Importación de Recursos Compilados (.qrc -> .py)
try:
    # Busca resources_rc.py en el mismo directorio (src/ui) usando import relativo
    from . import resources_rc
    print("Archivo de recursos 'resources_rc.py' importado correctamente.")
except ImportError:
    # Manejo de error si el archivo no existe
    print("ADVERTENCIA: No se encontró 'resources_rc.py'. "
          "Asegúrate de haber compilado 'iconos.qrc' usando:\n"
          "pyrcc5 src/ui/assets/iconos.qrc -o src/ui/resources_rc.py\n"
          "Los iconos definidos en el .ui pueden no cargarse.")
    # La aplicación podría continuar pero sin iconos cargados desde Python

# Determinar la ruta al archivo .ui de forma relativa a este script
ui_path = os.path.join(os.path.dirname(__file__), 'ui_files', 'Main_Window.ui')

class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación para procesar y renombrar
    imágenes escaneadas de guías de envío.
    """

    def __init__(self):
        """Inicializa la ventana principal, carga la UI y conecta eventos."""
        super(MainWindow, self).__init__()

        # --- El diccionario self.archivos_cargados ya NO se usa ---

        # Configurar la interfaz de usuario
        self._cargar_ui() # Carga el archivo .ui

        # Salir si la carga de UI falló (verificado dentro de _cargar_ui)
        if not hasattr(self, 'centralwidget'):
            # El mensaje de error ya se mostró en _cargar_ui
            print("Error fatal post-carga: La UI no parece haberse cargado correctamente. Saliendo.")
            # No se puede continuar sin la UI base
            sys.exit(1)

        self._conectar_eventos()      # Conecta señales (clics, cambios) a slots (métodos)
        self._inicializar_estado_ui() # Establece el estado inicial de los widgets

    # =======================================
    # ===== MÉTODOS DE INICIALIZACIÓN =====
    # =======================================

    def _cargar_ui(self):
        """Carga la interfaz de usuario desde el archivo .ui."""
        try:
            uic.loadUi(ui_path, self) # Carga la UI en la instancia actual (self)
            # Intentar encontrar el QLabel de previsualización después de cargar
            # findChild busca recursivamente en los widgets hijos
            self.label_preview = self.findChild(QLabel, "label_preview")
            if not self.label_preview:
                 print("Advertencia: No se encontró QLabel con objectName='label_preview' en el .ui. "
                       "La previsualización no funcionará.")
            # Podrías añadir búsquedas similares para otros widgets críticos si es necesario

        except FileNotFoundError:
            # Error si el archivo .ui no se encuentra en la ruta esperada
            mensaje = f"No se pudo encontrar el archivo UI en {ui_path}"
            print(f"Error Fatal: {mensaje}")
            QMessageBox.critical(None, "Error de Inicialización", mensaje) # None como padre si self no está listo
            sys.exit(1) # Salir inmediatamente
        except Exception as e:
            # Capturar cualquier otro error durante la carga (ej. XML mal formado)
            mensaje = f"Error al cargar la interfaz: {str(e)}"
            print(f"Error Fatal al cargar la interfaz: {e}")
            QMessageBox.critical(None, "Error de Inicialización", mensaje)
            sys.exit(1) # Salir inmediatamente

    def _conectar_eventos(self):
        """Conecta las señales de los widgets a los métodos (slots) correspondientes."""
        # Usar hasattr para evitar errores si un widget no se cargó correctamente desde el .ui
        if hasattr(self, 'boton_cargar'):
            self.boton_cargar.clicked.connect(self.cargar_imagenes)
        if hasattr(self, 'boton_procesar'):
            self.boton_procesar.clicked.connect(self.procesar_seleccionados)
        if hasattr(self, 'boton_seleccionar_todo'):
            self.boton_seleccionar_todo.clicked.connect(self.seleccionar_todo)
        if hasattr(self, 'boton_deseleccionar'):
            self.boton_deseleccionar.clicked.connect(self.deseleccionar_todo)

        # Conexiones para la lista de imágenes (usa el nombre del .ui: 'lista_imagenes')
        if hasattr(self, 'lista_imagenes'):
             self.lista_imagenes.itemClicked.connect(self.mostrar_detalles_item)
             # itemChanged se dispara cuando algo del item cambia (ej. estado del check)
             self.lista_imagenes.itemChanged.connect(self.actualizar_estado_ui)
        else:
            # Advertir si el widget crítico no existe
            print("Error Crítico: No se encontró el widget 'lista_imagenes' en la UI.")
            # Podrías deshabilitar funciones o mostrar un mensaje al usuario

        # Añadir conexiones para botones de siguiente/anterior imagen si existen
        # if hasattr(self, 'boton_siguiente_imagen'): self.boton_siguiente_imagen.clicked.connect(self._navegar_siguiente_imagen)
        # if hasattr(self, 'boton_volver_imagen'): self.boton_volver_imagen.clicked.connect(self._navegar_imagen_anterior)

    def _inicializar_estado_ui(self):
        """Configura el estado inicial de los widgets de la interfaz."""
        # Deshabilitar botones que dependen de selección/carga
        if hasattr(self, 'boton_procesar'):
            self.boton_procesar.setEnabled(False)

        # Limpiar y poner texto inicial en el área de previsualización
        if self.label_preview: # Verifica si label_preview fue encontrado en _cargar_ui
            self.label_preview.clear()
            self.label_preview.setText("Selecciona un archivo para previsualizar.")
            self.label_preview.setAlignment(Qt.AlignCenter) # Centrar texto/imagen

        # Configurar tooltips (textos de ayuda al pasar el mouse)
        if hasattr(self, 'boton_cargar'):
            self.boton_cargar.setToolTip("Cargar archivos de imagen escaneados (jpg, png, etc.)")
        if hasattr(self, 'boton_procesar'):
            self.boton_procesar.setToolTip("Extraer número de guía y renombrar los archivos seleccionados")
        if hasattr(self, 'boton_seleccionar_todo'):
            self.boton_seleccionar_todo.setToolTip("Marcar todos los archivos de la lista")
        if hasattr(self, 'boton_deseleccionar'):
            self.boton_deseleccionar.setToolTip("Desmarcar todos los archivos de la lista")
        if hasattr(self, 'linea_edicion_texto'):
             self.linea_edicion_texto.setToolTip("Editar nombre manualmente si falla el reconocimiento (Funcionalidad futura)")
             self.linea_edicion_texto.setEnabled(False) # Deshabilitado por defecto
        if hasattr(self, 'boton_guardar'):
             self.boton_guardar.setToolTip("Guardar el nombre editado manualmente (Funcionalidad futura)")
             self.boton_guardar.setEnabled(False) # Deshabilitado por defecto

    # ====================================
    # ===== MÉTODOS DE GESTIÓN DE UI =====
    # ====================================

    def actualizar_estado_ui(self, item=None): # item es opcional, puede venir de la señal itemChanged
        """Actualiza el estado habilitado de los botones según la selección actual."""
        # Comprobar si lista_imagenes existe antes de usarla
        if not hasattr(self, 'lista_imagenes'):
            return # No hacer nada si la lista no existe

        items_seleccionados = self.obtener_items_seleccionados()
        hay_seleccion = len(items_seleccionados) > 0

        # Habilitar/deshabilitar el botón de procesar
        if hasattr(self, 'boton_procesar'):
            self.boton_procesar.setEnabled(hay_seleccion)

        # Podrías añadir lógica para habilitar edición manual si solo 1 item está seleccionado
        # if hasattr(self, 'linea_edicion_texto'): self.linea_edicion_texto.setEnabled(len(items_seleccionados) == 1)
        # if hasattr(self, 'boton_guardar'): self.boton_guardar.setEnabled(len(items_seleccionados) == 1)

    def _set_controles_habilitados(self, habilitado: bool):
        """Método auxiliar para habilitar/deshabilitar controles durante operaciones largas."""
        # Lista de widgets a habilitar/deshabilitar
        widgets_a_controlar = [
            'boton_cargar', 'boton_seleccionar_todo', 'boton_deseleccionar',
            'lista_imagenes', 'boton_procesar' # Incluir boton_procesar aquí
            # Añadir 'linea_edicion_texto', 'boton_guardar' si se implementan
        ]
        for nombre_widget in widgets_a_controlar:
            if hasattr(self, nombre_widget):
                widget = getattr(self, nombre_widget)
                widget.setEnabled(habilitado)

        # Re-evaluar estado de botones dependientes de selección cuando se HABILITAN los controles
        if habilitado:
            self.actualizar_estado_ui()
        # Si se deshabilitan, el botón procesar (y otros) ya fueron deshabilitados en el bucle

    # ===========================================
    # ===== MÉTODOS DE CARGA DE IMÁGENES =====
    # ===========================================

    def cargar_imagenes(self):
        """Abre un diálogo para seleccionar imágenes y las carga en la lista."""
        # Comprobar si lista_imagenes existe
        if not hasattr(self, 'lista_imagenes'):
            QMessageBox.critical(self, "Error", "El componente lista de imágenes no está disponible.")
            return

        # Directorio inicial sugerido (puede ser el último usado, home, o vacío)
        directorio_inicial = QDir.homePath() # O usa "" para el directorio por defecto del sistema

        archivos, _ = QFileDialog.getOpenFileNames(
            self, "Abrir archivos de guías escaneadas", directorio_inicial,
            "Archivos de imagen (*.jpg *.jpeg *.png *.bmp *.tif *.tiff);;Todos los archivos (*)" # Filtros
        )

        if not archivos: # Si el usuario presiona Cancelar
            print("Carga de archivos cancelada.")
            return

        # Limpiar estado actual antes de cargar nuevos archivos
        self.lista_imagenes.clear()
        # self.archivos_cargados ya no existe
        if self.label_preview:
            self.label_preview.clear()
            self.label_preview.setText("Previsualización") # Texto placeholder

        # Añadir cada archivo válido a la lista
        archivos_cargados_count = 0
        for ruta_completa in archivos:
            if os.path.exists(ruta_completa) and os.path.isfile(ruta_completa):
                self._agregar_item_a_lista(ruta_completa)
                archivos_cargados_count += 1
            else:
                 print(f"Advertencia: Archivo no encontrado o no es un archivo válido '{ruta_completa}', omitido.")
                 # Considerar mostrar un mensaje si *ningún* archivo es válido

        print(f"Se cargaron {archivos_cargados_count} archivos.")
        # Actualizar estado de la UI (ej. habilitar/deshabilitar botones)
        self.actualizar_estado_ui()

    def _agregar_item_a_lista(self, ruta_completa):
        """Crea un QListWidgetItem, le asocia la ruta y lo añade a la lista."""
        nombre_archivo = os.path.basename(ruta_completa)
        item = QListWidgetItem(nombre_archivo)
        # Configurar flags: Habilitado, Seleccionable, Chequeable
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked) # Estado inicial no chequeado

        # --- Almacenar la ruta completa DENTRO del item ---
        item.setData(Qt.UserRole, ruta_completa)

        # Añadir el item al QListWidget 'lista_imagenes'
        self.lista_imagenes.addItem(item)

    # ======================================
    # ===== MÉTODOS DE VISUALIZACIÓN =====
    # ======================================

    def mostrar_detalles_item(self, item: QListWidgetItem):
        """Muestra la previsualización de la imagen del item seleccionado."""
        if not item: # Si no hay item seleccionado (ej. al limpiar lista)
            return

        # Si el widget de previsualización no existe, no podemos mostrar nada
        if not self.label_preview:
            print("Debug: Intento de mostrar detalles pero label_preview no existe.")
            return

        # --- Obtener la ruta completa DESDE los datos del item ---
        ruta_completa = item.data(Qt.UserRole)

        # Actualizar el QLabel que muestra el nombre del archivo (si existe)
        if hasattr(self, 'label_nombre_archivo'):
            self.label_nombre_archivo.setText(item.text()) # Mostrar texto actual del item

        # Validar la ruta obtenida
        if not ruta_completa:
            print(f"Error: No se encontró ruta asociada al item '{item.text()}' usando item.data(Qt.UserRole)")
            self.label_preview.setText("Error interno: Ruta no encontrada.")
            self.label_preview.setAlignment(Qt.AlignCenter)
            return

        # Validar si el archivo aún existe en esa ruta
        if not os.path.exists(ruta_completa):
            print(f"Error: El archivo '{ruta_completa}' asociado al item ya no existe.")
            self.label_preview.setText(f"Archivo no encontrado:\n{os.path.basename(ruta_completa)}")
            self.label_preview.setAlignment(Qt.AlignCenter)
            return

        # Intentar cargar y mostrar la imagen
        try:
            pixmap = QPixmap(ruta_completa)
            # Verificar si QPixmap pudo cargar la imagen
            if pixmap.isNull():
                 print(f"Error: QPixmap no pudo cargar la imagen '{ruta_completa}' (formato inválido o archivo corrupto?)")
                 self.label_preview.setText(f"Error al cargar imagen:\n{os.path.basename(ruta_completa)}\n(¿Formato inválido?)")
                 self.label_preview.setAlignment(Qt.AlignCenter)
            else:
                # Si se cargó bien, mostrarla escalada
                self._mostrar_imagen_en_preview(pixmap)
        except Exception as e:
            # Capturar cualquier otra excepción durante la carga del QPixmap
            print(f"Excepción al cargar QPixmap para '{ruta_completa}': {e}")
            self.label_preview.setText(f"Error al mostrar:\n{os.path.basename(ruta_completa)}")
            self.label_preview.setAlignment(Qt.AlignCenter)

    def _mostrar_imagen_en_preview(self, pixmap: QPixmap):
        """Escala y muestra un QPixmap en el QLabel 'label_preview'."""
        if not self.label_preview: return # Salir si el label no existe

        # Escalar manteniendo la proporción aspectual al tamaño actual del QLabel
        # Usar .size() para obtener el tamaño del QLabel dinámicamente
        scaled_pixmap = pixmap.scaled(
            self.label_preview.size(), # Usar el tamaño del QLabel como límite
            Qt.KeepAspectRatio,        # Mantener proporciones
            Qt.SmoothTransformation    # Mejor calidad de escalado
        )
        self.label_preview.setPixmap(scaled_pixmap)
        self.label_preview.setAlignment(Qt.AlignCenter) # Centrar la imagen escalada

    # ===================================
    # ===== MÉTODOS DE SELECCIÓN =====
    # ===================================

    def obtener_items_seleccionados(self) -> list[QListWidgetItem]:
        """Devuelve una lista con los QListWidgetItems actualmente chequeados."""
        # Salir si lista_imagenes no existe
        if not hasattr(self, 'lista_imagenes'):
            return []

        seleccionados = []
        # Iterar por el número de items en la lista
        for i in range(self.lista_imagenes.count()):
            item = self.lista_imagenes.item(i)
            # Comprobar si el item existe y está chequeado
            if item and item.checkState() == Qt.Checked:
                seleccionados.append(item)
        return seleccionados

    def seleccionar_todo(self):
        """Marca todos los items habilitados en la lista como chequeados."""
        self._cambiar_seleccion_todos(Qt.Checked)

    def deseleccionar_todo(self):
        """Marca todos los items en la lista como no chequeados."""
        self._cambiar_seleccion_todos(Qt.Unchecked)

    def _cambiar_seleccion_todos(self, estado: Qt.CheckState):
        """Aplica un estado de check (Checked o Unchecked) a todos los items habilitados."""
        # Salir si lista_imagenes no existe
        if not hasattr(self, 'lista_imagenes'):
            return

        # Iterar y cambiar estado
        for i in range(self.lista_imagenes.count()):
            item = self.lista_imagenes.item(i)
            # Cambiar solo si el item existe y está habilitado
            if item and (item.flags() & Qt.ItemIsEnabled):
                item.setCheckState(estado)

        # Actualizar estado de la UI (ej. botón procesar) después de cambiar selección
        self.actualizar_estado_ui()

    # =======================================
    # ===== MÉTODOS DE PROCESAMIENTO =====
    # =======================================

    def procesar_seleccionados(self):
        """Inicia el procesamiento (OCR/Barcode y renombrado) para los items seleccionados."""
        items_a_procesar = self.obtener_items_seleccionados()
        if not items_a_procesar:
            QMessageBox.warning(self, "Sin Selección",
                                 "Por favor, selecciona al menos un archivo para procesar.")
            return

        total_items = len(items_a_procesar)
        # Diccionario para contabilizar resultados
        resultados = {
            "exito": 0, "fallo_extraccion": 0, "fallo_renombrado": 0,
            "ya_existe": 0, "archivo_no_encontrado": 0, "errores_detalle": []
        }

        # Deshabilitar controles durante el proceso
        self._set_controles_habilitados(False)

        # --- Barra de Progreso ---
        progreso = 0
        # Crear el diálogo de progreso como hijo de la ventana principal (self)
        progress_dialog = QProgressDialog("Procesando archivos...", "Cancelar", 0, total_items, self)
        progress_dialog.setWindowTitle("Procesando")
        progress_dialog.setWindowModality(Qt.WindowModal) # Bloquea interacción con la ventana principal
        progress_dialog.setMinimumDuration(500)          # Solo mostrar si tarda más de 0.5 segundos
        progress_dialog.setValue(0)                      # Valor inicial

        try:
            # Iterar sobre la copia de la lista para evitar problemas si se modifica durante el proceso
            for item in items_a_procesar[:]:
                 # Actualizar barra de progreso
                 progreso += 1
                 progress_dialog.setValue(progreso)
                 # Mostrar nombre actual del item en la barra
                 progress_dialog.setLabelText(f"Procesando {progreso}/{total_items}: {item.text()}")

                 # Permitir que la UI se refresque y detectar si se presionó "Cancelar"
                 QtWidgets.QApplication.processEvents()
                 if progress_dialog.wasCanceled():
                      print("Proceso cancelado por el usuario.")
                      resultados["errores_detalle"].insert(0, "Proceso cancelado por el usuario.") # Añadir al inicio
                      break # Salir del bucle for

                 # Procesar el item individual (llamada a la función que hace el trabajo)
                 resultado_item = self._procesar_item(item)

                 # Contabilizar resultados basados en el diccionario devuelto por _procesar_item
                 tipo_resultado = resultado_item.get("tipo", "desconocido") # Usar .get con default
                 if tipo_resultado == "exito":              resultados["exito"] += 1
                 elif tipo_resultado == "ya_existe":        resultados["ya_existe"] += 1
                 elif tipo_resultado == "no_encontrado":    resultados["archivo_no_encontrado"] += 1
                 elif tipo_resultado == "extraccion":       resultados["fallo_extraccion"] += 1
                 elif tipo_resultado == "renombrado":       resultados["fallo_renombrado"] += 1

                 # Añadir mensaje de error/advertencia a detalles si no fue éxito
                 if tipo_resultado != "exito":
                     mensaje = resultado_item.get("mensaje", "Error desconocido")
                     if mensaje: # Asegurarse que hay un mensaje
                        resultados["errores_detalle"].append(mensaje)

        except Exception as e:
            # Capturar cualquier error inesperado que ocurra DENTRO del bucle try
            print(f"Error inesperado durante el procesamiento: {e}")
            # Añadir traceback al log si es posible: import traceback; traceback.print_exc()
            QMessageBox.critical(self, "Error en Procesamiento", f"Ocurrió un error inesperado: {str(e)}")
            resultados["errores_detalle"].append(f"Error inesperado general durante el bucle: {str(e)}")
        finally:
            # Este bloque SIEMPRE se ejecuta, haya error o no, o si se cancela
            progress_dialog.close() # Cerrar el diálogo de progreso
            self._set_controles_habilitados(True) # Habilitar controles de nuevo
            # Mostrar el resumen del procesamiento
            self._mostrar_resumen_procesamiento(resultados, total_items)

    def _procesar_item(self, item: QListWidgetItem) -> dict:
        """
        Procesa un item individual: obtiene ruta, extrae número, renombra.
        Devuelve un diccionario con:
        {"tipo": "exito"|"ya_existe"|"no_encontrado"|"extraccion"|"renombrado", "mensaje": str}
        """
        # Resetear apariencia del item al inicio del procesamiento
        item.setBackground(QtGui.QColor('white'))
        item.setForeground(QtGui.QColor('black'))

        # --- 1. Obtener la ruta original desde los datos del item ---
        ruta_original = item.data(Qt.UserRole)
        nombre_actual_item = item.text() # Nombre que se muestra actualmente

        # --- 2. Validar la ruta y existencia del archivo ---
        if not ruta_original:
            mensaje = f"{nombre_actual_item}: Error interno - Ruta no asociada."
            self._marcar_item_error(item, f"{nombre_actual_item} [Error Ruta]", QtGui.QColor(255, 0, 0)) # Rojo brillante
            return {"tipo": "no_encontrado", "mensaje": mensaje}

        if not os.path.exists(ruta_original):
            mensaje = f"{nombre_actual_item}: Archivo no encontrado en la ruta '{ruta_original}' (¿movido o eliminado?)."
            self._marcar_item_error(item, f"{nombre_actual_item} [No encontrado]", QtGui.QColor(255, 204, 204)) # Rojo pálido
            return {"tipo": "no_encontrado", "mensaje": mensaje}

        # --- 3. Extraer número de guía (Llamada al módulo Core) ---
        print(f"Procesando item: {nombre_actual_item}, Ruta: {ruta_original}") # Log
        numero_guia = None
        try:
            # Llamar a la función del image_processor
            numero_guia = image_processor.get_guide_number(ruta_original)
            print(f"  Resultado OCR/BC: '{numero_guia}' (Tipo: {type(numero_guia)})") # Log detallado
        except Exception as e:
            # Capturar errores específicos de las librerías OCR/Barcode si es posible
            print(f"  Error durante get_guide_number: {e}")
            # import traceback; traceback.print_exc() # Para más detalles del error
            mensaje = f"{nombre_actual_item}: Error extrayendo número - {str(e)}"
            self._marcar_item_error(item, f"{nombre_actual_item} [Error OCR/BC]", QtGui.QColor(255, 153, 153)) # Rojo más fuerte
            return {"tipo": "extraccion", "mensaje": mensaje}

        # --- 4. Validar el número de guía extraído ---
        if not numero_guia: # Si devuelve None o vacío
            mensaje = f"{nombre_actual_item}: No se pudo extraer número de guía (OCR/Barcode)."
            self._marcar_item_error(item, f"{nombre_actual_item} [No reconocido]", QtGui.QColor(255, 230, 204)) # Naranja pálido
            return {"tipo": "extraccion", "mensaje": mensaje}

        # Limpiar el número (quitar espacios, caracteres no deseados)
        # Asegurarse que sea string antes de limpiar
        numero_guia_str = str(numero_guia).strip()
        numero_guia_limpio = "".join(filter(str.isalnum, numero_guia_str))

        if not numero_guia_limpio:
             mensaje = f"{nombre_actual_item}: Número de guía inválido después de limpiar ('{numero_guia_str}')."
             self._marcar_item_error(item, f"{nombre_actual_item} [Guía inválida]", QtGui.QColor(255, 230, 204))
             return {"tipo": "extraccion", "mensaje": mensaje}
        print(f"  Número de guía limpio: '{numero_guia_limpio}'") # Log

        # --- 5. Preparar Renombrado ---
        directorio = os.path.dirname(ruta_original)
        # Obtener extensión del nombre *actual* del item para conservarla
        _, extension = os.path.splitext(nombre_actual_item)
        nuevo_nombre = f"{numero_guia_limpio}{extension}"
        nueva_ruta = os.path.join(directorio, nuevo_nombre)

        # Normalizar rutas para comparación fiable (maneja / vs \)
        ruta_original_norm = os.path.normpath(ruta_original)
        nueva_ruta_norm = os.path.normpath(nueva_ruta)

        # --- 6. Verificar si el renombrado es necesario ---
        if nuevo_nombre == nombre_actual_item:
            print(f"  El archivo '{nombre_actual_item}' ya tiene el nombre correcto.")
            self._marcar_item_estado(item, f"{nombre_actual_item} [Ya correcto]", QtGui.QColor(220, 220, 220)) # Gris
            item.setCheckState(Qt.Unchecked) # Desmarcar si ya está bien
            # Actualizar la ruta interna por si acaso (ej. si cambió normalización)
            item.setData(Qt.UserRole, nueva_ruta)
            return {"tipo": "exito", "mensaje": ""}

        # --- 7. Verificar si el nuevo nombre ya existe ---
        if os.path.exists(nueva_ruta_norm):
            print(f"  Advertencia: El destino '{nuevo_nombre}' ya existe.")
            mensaje = f"{nombre_actual_item}: El destino '{nuevo_nombre}' ya existe."
            self._marcar_item_error(item, f"{nombre_actual_item} [Destino existe]", QtGui.QColor(255, 255, 204)) # Amarillo pálido
            return {"tipo": "ya_existe", "mensaje": mensaje}

        # --- 8. Intentar Renombrar (Llamada al módulo Core) ---
        print(f"  Intentando renombrar: '{ruta_original}' -> '{nueva_ruta}'") # Log
        exito_renombrado, mensaje_error = file_operations.rename_scan(ruta_original, nueva_ruta)

        if exito_renombrado:
            print(f"  Renombrado con éxito a '{nuevo_nombre}'")
            # Éxito: Actualizar UI y datos internos
            self._marcar_item_estado(item, nuevo_nombre, QtGui.QColor(204, 255, 204)) # Verde pálido
            item.setCheckState(Qt.Unchecked) # Desmarcar tras éxito
            # --- MUY IMPORTANTE: Actualizar la ruta guardada DENTRO del item ---
            item.setData(Qt.UserRole, nueva_ruta)
            return {"tipo": "exito", "mensaje": ""}
        else:
            # Fallo: Mostrar error
            print(f"  Error al renombrar: {mensaje_error}")
            mensaje = f"{nombre_actual_item}: Error renombrando - {mensaje_error}"
            self._marcar_item_error(item, f"{nombre_actual_item} [Error al renombrar]", QtGui.QColor(255, 153, 153))
            return {"tipo": "renombrado", "mensaje": mensaje}

    # --- Métodos auxiliares para marcar items en la lista ---
    def _marcar_item_error(self, item: QListWidgetItem, texto: str, color: QtGui.QColor):
        """Aplica estilo visual a un item para indicar error o advertencia."""
        if not item: return # Seguridad
        item.setText(texto)
        item.setBackground(color)
        # Poner texto blanco sobre fondos oscuros/rojos para legibilidad
        if color.lightnessF() < 0.5 or (color.red() > 180 and color.green() < 100):
             item.setForeground(QtGui.QColor('white'))
        else:
             item.setForeground(QtGui.QColor('black'))

    def _marcar_item_estado(self, item: QListWidgetItem, texto: str, color: QtGui.QColor):
         """Aplica estilo visual a un item para indicar un estado no erróneo."""
         if not item: return
         item.setText(texto)
         item.setBackground(color)
         item.setForeground(QtGui.QColor('black')) # Texto negro por defecto

    # --- Mostrar Resumen Final ---
    def _mostrar_resumen_procesamiento(self, resultados: dict, total_seleccionados: int):
        """Muestra un QMessageBox con el resumen del procesamiento."""
        mensaje = f"Proceso completado para {total_seleccionados} archivos seleccionados.\n\n"
        mensaje += f"  - Éxito / Ya correctos: {resultados['exito']}\n"
        mensaje += f"  - Fallo extracción (OCR/BC): {resultados['fallo_extraccion']}\n"
        mensaje += f"  - Fallo al renombrar (Error OS): {resultados['fallo_renombrado']}\n"
        mensaje += f"  - Omitidos (Destino ya existe): {resultados['ya_existe']}\n"
        mensaje += f"  - Omitidos (Archivo no encontrado): {resultados['archivo_no_encontrado']}\n"

        fallos_totales = (total_seleccionados - resultados['exito'])

        # Crear el QMessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Resultado del Proceso")
        msg_box.setText(mensaje) # Texto principal del resumen

        # Determinar icono basado en si hubo fallos
        if fallos_totales > 0:
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(QMessageBox.Information)

        # Añadir detalles si existen errores/advertencias
        if resultados["errores_detalle"]:
            # Crear un área de texto desplazable para los detalles
            scroll_text = QTextEdit()
            scroll_text.setReadOnly(True)
            # Unir detalles con saltos de línea, usando un guion para cada uno
            detalles_str = "\n".join([f"- {e}" for e in resultados["errores_detalle"]])
            scroll_text.setText("Detalles de errores/advertencias:\n" + detalles_str)
            scroll_text.setMinimumHeight(150) # Darle una altura mínima

            # Añadir el QTextEdit al layout del QMessageBox
            # El layout se obtiene con msg_box.layout()
            # Añadir como un widget nuevo en la siguiente fila disponible
            try:
                msg_box.layout().addWidget(scroll_text, msg_box.layout().rowCount(), 0, 1, msg_box.layout().columnCount())
                # Hacer el diálogo más ancho para acomodar el texto
                msg_box.setStyleSheet("QMessageBox { messagebox-width: 500px; }")
            except Exception as layout_e:
                 # Fallback si falla añadir el widget (raro)
                 print(f"Error añadiendo detalles al QMessageBox layout: {layout_e}")
                 # Usar setDetailedText como alternativa menos flexible
                 msg_box.setDetailedText("\n".join(resultados["errores_detalle"]))

        # Mostrar el diálogo
        msg_box.exec_()

    # ==================================
    # ===== EVENTOS DE LA VENTANA =====
    # ==================================

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Se intercepta el evento de cierre de la ventana para pedir confirmación."""
        reply = QMessageBox.question(self, 'Confirmar Salida',
                                     "¿Estás seguro de que quieres salir de la aplicación?",
                                     QMessageBox.Yes | QMessageBox.No, # Botones Sí y No
                                     QMessageBox.No) # Botón por defecto es No

        if reply == QMessageBox.Yes:
            print("Cerrando la aplicación...")
            event.accept() # Continuar con el cierre
        else:
            print("Cierre cancelado.")
            event.ignore() # Detener el proceso de cierre

