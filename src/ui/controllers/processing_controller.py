"""
Controlador para el procesamiento de archivos.
"""
from typing import Dict, List, Callable
from PyQt5.QtWidgets import QWidget, QProgressDialog, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem

from src.ui.components.item_processor import ItemProcessor

class ProcessingController:
    """Gestiona el procesamiento en lote de archivos."""
    
    def __init__(self, parent_widget: QWidget):
        """
        Inicializa el controlador.
        
        Args:
            parent_widget: Widget padre para diálogos
        """
        self.parent = parent_widget
    
    def process_items(self, items: List[QListWidgetItem], 
                      ui_update_callback: Callable) -> Dict:
        """
        Procesa una lista de items mostrando progreso.
        
        Args:
            items: Lista de items a procesar
            ui_update_callback: Función para habilitar/deshabilitar UI
            
        Returns:
            Diccionario con resultados del proceso
        """
        if not items:
            return {}
            
        total_items = len(items)
        results = self._initialize_results()
        
        ui_update_callback(False)  # Deshabilitar UI durante el proceso
        progress_dialog = self._create_progress_dialog(total_items)
        
        try:
            self._process_items_with_progress(items, progress_dialog, results)
        except Exception as e:
            print(f"Error inesperado durante el procesamiento: {e}")
            results["errores_detalle"].append(f"Error inesperado general: {str(e)}")
        finally:
            progress_dialog.close()
            ui_update_callback(True)  # Rehabilitar UI
            
        return results
    
    def _initialize_results(self) -> Dict:
        """
        Inicializa el diccionario de resultados.
        
        Returns:
            Diccionario vacío para almacenar resultados
        """
        return {
            "exito": 0, 
            "fallo_extraccion": 0, 
            "fallo_renombrado": 0, 
            "ya_existe": 0, 
            "archivo_no_encontrado": 0, 
            "errores_detalle": []
        }
    
    def _create_progress_dialog(self, total_items: int) -> QProgressDialog:
        """
        Crea y configura el diálogo de progreso.
        
        Args:
            total_items: Número total de items a procesar
            
        Returns:
            Diálogo de progreso configurado
        """
        progress_dialog = QProgressDialog("Procesando archivos...", "Cancelar", 0, total_items, self.parent)
        progress_dialog.setWindowTitle("Procesando")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(500)
        progress_dialog.setValue(0)
        return progress_dialog
    
    def _process_items_with_progress(self, items: List[QListWidgetItem], 
                                   progress_dialog: QProgressDialog, 
                                   results: Dict) -> None:
        """
        Procesa los items mostrando progreso.
        
        Args:
            items: Lista de items a procesar
            progress_dialog: Diálogo de progreso
            results: Diccionario para almacenar resultados
        """
        progress = 0
        for item in items[:]:
            progress += 1
            progress_dialog.setValue(progress)
            progress_dialog.setLabelText(f"Procesando {progress}/{len(items)}: {item.text()}")
            QApplication.processEvents()
            
            if progress_dialog.wasCanceled():
                results["errores_detalle"].insert(0, "Proceso cancelado por el usuario.")
                break
                
            item_result = ItemProcessor.process_item(item)
            self._update_result_counters(item_result, results)
    
    def _update_result_counters(self, item_result: Dict, results: Dict) -> None:
        """
        Actualiza los contadores de resultados según el tipo de resultado.
        
        Args:
            item_result: Resultado del procesamiento de un item
            results: Diccionario de resultados acumulados
        """
        result_type = item_result.get("tipo", "desconocido")
        
        if result_type == "exito":              
            results["exito"] += 1
        elif result_type == "ya_existe":        
            results["ya_existe"] += 1
        elif result_type == "no_encontrado":    
            results["archivo_no_encontrado"] += 1
        elif result_type == "extraccion":       
            results["fallo_extraccion"] += 1
        elif result_type == "renombrado":       
            results["fallo_renombrado"] += 1
            
        if result_type != "exito":
            message = item_result.get("mensaje", "Error desconocido")
            if message: 
                results["errores_detalle"].append(message)