"""
Funciones auxiliares para manejo de archivos en la UI.
"""
import os
from typing import List, Tuple
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtCore import QDir

def get_image_files_dialog(parent: QWidget) -> List[str]:
    """
    Muestra un diálogo para seleccionar archivos de imagen.
    
    Args:
        parent: Widget padre para el diálogo
        
    Returns:
        Lista de rutas de archivos seleccionados
    """
    initial_dir = QDir.homePath()
    files, _ = QFileDialog.getOpenFileNames(
        parent, "Abrir archivos de guías escaneadas", initial_dir,
        "Archivos de imagen (*.jpg *.jpeg *.png *.bmp *.tif *.tiff);;Todos los archivos (*)"
    )
    return files

def is_valid_filename(filename: str) -> Tuple[bool, str]:
    """
    Valida si un nombre de archivo es válido.
    
    Args:
        filename: Nombre a validar
        
    Returns:
        Tupla con (es_válido, mensaje_error)
    """
    if not filename:
        return False, "El nombre no puede estar vacío."
        
    # Caracteres prohibidos en nombres de archivo
    invalid_chars = r'[\<\>\:\"\/\\\|\?\*]'
    import re
    if re.search(invalid_chars, filename):
        return False, f"El nombre contiene caracteres inválidos."
        
    return True, ""

def split_filename(filename: str) -> Tuple[str, str]:
    """
    Divide un nombre de archivo en nombre base y extensión.
    
    Args:
        filename: Nombre de archivo completo
        
    Returns:
        Tupla con (nombre_base, extensión)
    """
    return os.path.splitext(filename)