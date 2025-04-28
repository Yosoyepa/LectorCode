"""
Controlador para la lista de items.
"""
import os
from typing import List, Optional, Callable
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt

class ItemListController:
    """Gestiona la lista de items de imágenes."""
    
    def __init__(self, list_widget: QListWidget):
        """
        Inicializa el controlador.
        
        Args:
            list_widget: Widget de lista a controlar
        """
        self.list_widget = list_widget
    
    def add_file(self, file_path: str) -> None:
        """
        Añade un archivo a la lista.
        
        Args:
            file_path: Ruta del archivo a añadir
        """
        filename = os.path.basename(file_path)
        item = QListWidgetItem(filename)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, file_path)
        self.list_widget.addItem(item)
    
    def load_files(self, file_paths: List[str]) -> int:
        """
        Carga múltiples archivos en la lista.
        
        Args:
            file_paths: Lista de rutas de archivos
            
        Returns:
            Número de archivos cargados exitosamente
        """
        loaded_count = 0
        
        for path in file_paths:
            if os.path.exists(path) and os.path.isfile(path):
                self.add_file(path)
                loaded_count += 1
            else:
                print(f"Advertencia: Archivo no encontrado '{path}', omitido.")
                
        return loaded_count
    
    def clear_list(self) -> None:
        """Limpia todos los items de la lista."""
        self.list_widget.clear()
    
    def get_checked_items(self) -> List[QListWidgetItem]:
        """
        Obtiene los items marcados con checkmark.
        
        Returns:
            Lista de items marcados
        """
        checked_items = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.checkState() == Qt.Checked:
                checked_items.append(item)
                
        return checked_items
    
    def select_all(self) -> None:
        """Marca todos los items de la lista."""
        self._change_all_selection(Qt.Checked)
    
    def deselect_all(self) -> None:
        """Desmarca todos los items de la lista."""
        self._change_all_selection(Qt.Unchecked)
    
    def _change_all_selection(self, state: Qt.CheckState) -> None:
        """
        Cambia el estado de selección de todos los items.
        
        Args:
            state: Estado de checkmark a aplicar
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and (item.flags() & Qt.ItemIsEnabled):
                item.setCheckState(state)
    
    def select_first_item(self) -> None:
        """Selecciona el primer item de la lista si existe."""
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
    
    def navigate_previous(self) -> None:
        """Navega al item anterior en la lista."""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            self.list_widget.setCurrentRow(current_row - 1)
    
    def navigate_next(self) -> None:
        """Navega al item siguiente en la lista."""
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(current_row + 1)
    
    def get_current_item(self) -> Optional[QListWidgetItem]:
        """
        Obtiene el item actualmente seleccionado.
        
        Returns:
            El item seleccionado o None si no hay selección
        """
        return self.list_widget.currentItem()
    
    def get_current_row(self) -> int:
        """
        Obtiene el índice de fila del item actualmente seleccionado.
        
        Returns:
            Índice de fila o -1 si no hay selección
        """
        return self.list_widget.currentRow()
    
    def get_item_count(self) -> int:
        """
        Obtiene el número total de items en la lista.
        
        Returns:
            Número de items
        """
        return self.list_widget.count()
    
    def connect_item_changed(self, callback: Callable) -> None:
        """
        Conecta un callback al evento de cambio de item.
        
        Args:
            callback: Función a llamar cuando cambia un item
        """
        self.list_widget.itemChanged.connect(callback)
    
    def connect_item_clicked(self, callback: Callable) -> None:
        """
        Conecta un callback al evento de clic en item.
        
        Args:
            callback: Función a llamar cuando se hace clic en un item
        """
        self.list_widget.itemClicked.connect(callback)
    
    def connect_current_item_changed(self, callback: Callable) -> None:
        """
        Conecta un callback al evento de cambio de item actual.
        
        Args:
            callback: Función a llamar cuando cambia el item actual
        """
        self.list_widget.currentItemChanged.connect(callback)