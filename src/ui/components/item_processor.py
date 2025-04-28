"""
Componente para procesar items en la lista.
"""
from typing import Dict, Optional
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.core import processing_handler
from src.utils.ui_helpers import mark_item_error, mark_item_status

class ItemProcessor:
    """Procesa items individuales usando processing_handler."""
    
    @staticmethod
    def process_item(item: QListWidgetItem) -> Dict:
        """
        Procesa un item individual utilizando el handler automático.
        
        Args:
            item: Item a procesar
            
        Returns:
            Diccionario con el resultado del procesamiento
        """
        # Restaurar apariencia
        item.setBackground(QColor('white'))
        item.setForeground(QColor('black'))
        
        # Obtener datos del item
        path = item.data(Qt.UserRole)
        current_name = item.text()
        
        # Verificar existencia de la ruta
        if not path:
            message = f"{current_name}: Error interno - Ruta no asociada."
            mark_item_error(item, f"{current_name} [Error Ruta]", QColor(255, 0, 0))
            return {"tipo": "no_encontrado", "mensaje": message}
        
        # Usar processing_handler para el procesamiento automático
        result = processing_handler.process_single_file_auto(path)
        status = result["status"]
        
        # Manejar diferentes estados de resultado
        if status == "success":
            # Éxito en el renombrado
            new_name = result["new_name"]
            new_path = result["new_path"]
            mark_item_status(item, new_name, QColor(204, 255, 204))
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, new_path)
            return {"tipo": "exito", "mensaje": ""}
            
        elif status == "no_rename_needed":
            # El archivo ya tiene el nombre correcto
            mark_item_status(item, f"{current_name} [Ya correcto]", QColor(220, 220, 220))
            item.setCheckState(Qt.Unchecked)
            return {"tipo": "exito", "mensaje": ""}
            
        elif status == "ocr_failed":
            # Fallo en extracción OCR/Barcode
            message = f"{current_name}: {result['message']}"
            mark_item_error(item, f"{current_name} [No reconocido]", QColor(255, 230, 204))
            return {"tipo": "extraccion", "mensaje": message}
            
        elif status == "target_exists":
            # El archivo destino ya existe
            message = f"{current_name}: {result['message']}"
            mark_item_error(item, f"{current_name} [Destino existe]", QColor(255, 255, 204))
            return {"tipo": "ya_existe", "mensaje": message}
            
        elif status == "rename_failed":
            # Fallo al renombrar
            message = f"{current_name}: {result['message']}"
            mark_item_error(item, f"{current_name} [Error al renombrar]", QColor(255, 153, 153))
            return {"tipo": "renombrado", "mensaje": message}
            
        else:  # "error" u otros estados no manejados
            message = f"{current_name}: {result.get('message', 'Error desconocido')}"
            mark_item_error(item, f"{current_name} [Error]", QColor(255, 153, 153))
            return {"tipo": "error", "mensaje": message}
    
    @staticmethod
    def rename_item_manual(item: QListWidgetItem, new_base_name: str) -> Dict:
        """
        Renombra un item manualmente.
        
        Args:
            item: Item a renombrar
            new_base_name: Nuevo nombre base sin extensión
            
        Returns:
            Diccionario con el resultado: {"success": bool, "message": str, ...}
        """
        path = item.data(Qt.UserRole)
        current_name = item.text()
        
        if not path:
            return {
                "success": False, 
                "message": f"El archivo original '{current_name}' no tiene una ruta válida asociada."
            }
            
        # Usar processing_handler para el renombrado manual
        result = processing_handler.rename_single_file_manual(
            path, current_name, new_base_name
        )
        
        return result
    
    @staticmethod
    def update_renamed_item(item: QListWidgetItem, new_name: str, new_path: str) -> None:
        """
        Actualiza un item después de un renombrado exitoso.
        
        Args:
            item: Item renombrado
            new_name: Nuevo nombre del archivo
            new_path: Nueva ruta del archivo
        """
        item.setText(new_name)
        item.setData(Qt.UserRole, new_path)
        item.setBackground(QColor(220, 255, 220))  # Verde muy pálido para indicar éxito
        item.setForeground(QColor('black'))