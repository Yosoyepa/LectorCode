"""
Componente para previsualización de imágenes.
"""
import os
from typing import Optional
from PyQt5.QtWidgets import QLabel, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class ImagePreviewComponent:
    """Gestiona la previsualización de imágenes."""
    
    def __init__(self, preview_label: QLabel, filename_label: Optional[QLabel] = None):
        """
        Inicializa el componente de previsualización.
        
        Args:
            preview_label: Label donde se mostrará la imagen 
            filename_label: Label opcional para mostrar el nombre del archivo
        """
        self.preview_label = preview_label
        self.filename_label = filename_label
    
    def show_preview(self, item: Optional[QListWidgetItem]) -> None:
        """
        Muestra la previsualización de la imagen del item dado.
        
        Args:
            item: Item de la lista a previsualizar
        """
        if not item:
            self.show_empty_preview()
            return
        
        file_path = item.data(Qt.UserRole)
        self.update_filename(item.text())
        
        if not file_path or not os.path.exists(file_path):
            self.show_error_preview(item.text(), file_path)
            return
            
        self.load_image_preview(file_path, item.text())
    
    def show_empty_preview(self) -> None:
        """Muestra un estado vacío en la previsualización."""
        if self.preview_label:
            self.preview_label.clear()
            self.preview_label.setText("Selecciona un archivo")
            self.preview_label.setAlignment(Qt.AlignCenter)
            
        if self.filename_label:
            self.filename_label.setText("-")
    
    def update_filename(self, name: str) -> None:
        """
        Actualiza el label con el nombre del archivo.
        
        Args:
            name: Nombre del archivo a mostrar
        """
        if self.filename_label:
            self.filename_label.setText(name)
    
    def show_error_preview(self, name: str, path: Optional[str]) -> None:
        """
        Muestra un mensaje de error en la previsualización.
        
        Args:
            name: Nombre del archivo
            path: Ruta del archivo (o None si no hay ruta)
        """
        if not self.preview_label:
            return
            
        message = f"Archivo no encontrado:\n{name}"
        if not path:
            message = "Error: Ruta no asociada."
            
        self.preview_label.setText(message)
        self.preview_label.setAlignment(Qt.AlignCenter)
    
    def load_image_preview(self, path: str, name: str) -> None:
        """
        Carga y muestra una imagen en la previsualización.
        
        Args:
            path: Ruta de la imagen a cargar
            name: Nombre del archivo para mostrar en caso de error
        """
        if not self.preview_label:
            return
            
        try:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                self.preview_label.setText(f"Error al cargar:\n{name}")
                self.preview_label.setAlignment(Qt.AlignCenter)
            else:
                self._display_image(pixmap)
        except Exception as e:
            print(f"Excepción al cargar QPixmap para '{path}': {e}")
            self.preview_label.setText(f"Error al mostrar:\n{name}")
            self.preview_label.setAlignment(Qt.AlignCenter)
    
    def _display_image(self, pixmap: QPixmap) -> None:
        """
        Escala y muestra un QPixmap en el QLabel de previsualización.
        
        Args:
            pixmap: Imagen a mostrar
        """
        if not self.preview_label:
            return
            
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.setAlignment(Qt.AlignCenter)