"""
Funciones auxiliares para manipulación de UI y widgets.
"""
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

def configure_tooltips(widget_owner: Any, tooltips: Dict[str, str]) -> None:
    """
    Configura tooltips para un conjunto de widgets.
    
    Args:
        widget_owner: Objeto que contiene los widgets como atributos
        tooltips: Diccionario con nombre_widget -> texto_tooltip
    """
    for widget_name, tooltip_text in tooltips.items():
        widget = getattr(widget_owner, widget_name, None)
        if widget:
            widget.setToolTip(tooltip_text)

def set_widgets_enabled(widget_owner: Any, widget_names: List[str], enabled: bool) -> None:
    """
    Habilita o deshabilita un conjunto de widgets.
    
    Args:
        widget_owner: Objeto que contiene los widgets como atributos
        widget_names: Lista de nombres de widgets a modificar
        enabled: True para habilitar, False para deshabilitar
    """
    for widget_name in widget_names:
        if hasattr(widget_owner, widget_name):
            widget = getattr(widget_owner, widget_name)
            widget.setEnabled(enabled)

def mark_item_error(item: Optional[QListWidgetItem], text: str, color: QColor) -> None:
    """
    Marca un item con un estado de error, ajustando el color de texto para contraste.
    
    Args:
        item: Item a marcar
        text: Texto a mostrar
        color: Color de fondo
    """
    if not item:
        return
        
    item.setText(text)
    item.setBackground(color)
    
    # Ajustar color de texto para contraste
    if color.lightnessF() < 0.5 or (color.red() > 180 and color.green() < 100):
        item.setForeground(QColor('white'))
    else:
        item.setForeground(QColor('black'))

def mark_item_status(item: Optional[QListWidgetItem], text: str, color: QColor) -> None:
    """
    Marca un item con un estado normal (texto negro sobre fondo de color).
    
    Args:
        item: Item a marcar
        text: Texto a mostrar
        color: Color de fondo
    """
    if not item:
        return
        
    item.setText(text)
    item.setBackground(color)
    item.setForeground(QColor('black'))

def clear_preview_widgets(label: Optional[QLabel], line_edit: Optional[QLineEdit]) -> None:
    """
    Limpia los widgets de previsualización.
    
    Args:
        label: Label de previsualización
        line_edit: Widget de edición de texto
    """
    if label:
        label.clear()
        label.setText("Selecciona un archivo para previsualizar.")
        label.setAlignment(Qt.AlignCenter)
    if line_edit:
        line_edit.clear()