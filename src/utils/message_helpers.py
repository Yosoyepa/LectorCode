"""
Funciones auxiliares para mostrar mensajes y diálogos.
"""
from typing import List, Optional
from PyQt5.QtWidgets import QMessageBox, QTextEdit, QWidget

def show_error_message(parent: QWidget, title: str, message: str) -> None:
    """
    Muestra un mensaje de error.
    
    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar
    """
    QMessageBox.critical(parent, title, message)

def show_warning_message(parent: QWidget, title: str, message: str) -> None:
    """
    Muestra un mensaje de advertencia.
    
    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar
    """
    QMessageBox.warning(parent, title, message)

def show_info_message(parent: QWidget, title: str, message: str) -> None:
    """
    Muestra un mensaje informativo.
    
    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar
    """
    QMessageBox.information(parent, title, message)

def confirm_action(parent: QWidget, title: str, message: str, 
                  default_button: QMessageBox.StandardButton = QMessageBox.No) -> bool:
    """
    Muestra un diálogo de confirmación sí/no.
    
    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar
        default_button: Botón por defecto seleccionado
        
    Returns:
        True si se confirma, False si se cancela
    """
    # Asegurarse de que default_button sea válido para QMessageBox.question
    if default_button not in [QMessageBox.Yes, QMessageBox.No]:
        default_button = QMessageBox.No
        
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No, 
        default_button
    )
    return reply == QMessageBox.Yes

def add_details_to_message_box(msg_box: QMessageBox, errors: List[str]) -> None:
    """
    Añade detalles de errores al cuadro de mensaje.
    
    Args:
        msg_box: Cuadro de mensaje a modificar
        errors: Lista de mensajes de error para mostrar
    """
    scroll_text = QTextEdit()
    scroll_text.setReadOnly(True)
    details_str = "\n".join([f"- {e}" for e in errors])
    scroll_text.setText("Detalles de errores/advertencias:\n" + details_str)
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
        msg_box.setDetailedText("\n".join(errors))

def create_processing_summary(parent: QWidget, results: dict, total_selected: int) -> None:
    """
    Crea y muestra un resumen del procesamiento realizado.
    
    Args:
        parent: Widget padre 
        results: Diccionario con resultados
        total_selected: Total de archivos seleccionados
    """
    mensaje = f"Proceso completado para {total_selected} archivos seleccionados.\n\n"
    mensaje += f"  - Éxito / Ya correctos: {results['exito']}\n"
    mensaje += f"  - Fallo extracción (OCR/BC): {results['fallo_extraccion']}\n"
    mensaje += f"  - Fallo al renombrar (Error OS): {results['fallo_renombrado']}\n"
    mensaje += f"  - Omitidos (Destino ya existe): {results['ya_existe']}\n"
    mensaje += f"  - Omitidos (Archivo no encontrado): {results['archivo_no_encontrado']}\n"
    
    failures = (total_selected - results['exito'])
    
    # Crear diálogo
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Resultado del Proceso")
    msg_box.setText(mensaje)
    msg_box.setIcon(QMessageBox.Warning if failures > 0 else QMessageBox.Information)
    
    # Añadir detalles si hay errores
    if results["errores_detalle"]:
        add_details_to_message_box(msg_box, results["errores_detalle"])
        
    msg_box.exec_()