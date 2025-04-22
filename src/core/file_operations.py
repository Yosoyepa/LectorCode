# src/core/file_operations.py
import os
import shutil
from pathlib import Path
from typing import Tuple, Optional

def validar_ruta_archivo(ruta_archivo: str) -> Tuple[bool, Optional[str]]:
    """
    Valida si existe una ruta de archivo.
    
    Args:
        ruta_archivo: Ruta completa del archivo
        
    Returns:
        Tuple[bool, Optional[str]]: (éxito, mensaje_error)
    """
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        return False, f"El archivo no existe: {ruta.name}"
    return True, None

def rename_scan(old_path: str, new_path: str) -> Tuple[bool, Optional[str]]:
    """
    Renombra o mueve un archivo de escaneo.

    Args:
        old_path: Ruta completa del archivo original.
        new_path: Nueva ruta completa deseada para el archivo.

    Returns:
        Tuple[bool, Optional[str]]: (éxito, mensaje_error)
    """
    ruta_original = Path(old_path)
    ruta_nueva = Path(new_path)
    
    # Validar ruta original
    valido, error = validar_ruta_archivo(old_path)
    if not valido:
        print(f"Error de validación: {error}")
        return False, error
    
    # Crear directorio padre para la nueva ruta si no existe
    ruta_nueva.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Usar shutil.move es más robusto que os.rename, funciona entre discos
        shutil.move(str(ruta_original), str(ruta_nueva))
        print(f"Archivo renombrado/movido: '{ruta_original.name}' -> '{ruta_nueva.name}'")
        return True, None
    except OSError as e:
        error_msg = f"Error de OS al renombrar '{ruta_original.name}': {e}"
        print(error_msg)
        return False, str(e)
    except Exception as e:
        error_msg = f"Error inesperado al renombrar '{ruta_original.name}': {e}"
        print(error_msg)
        return False, str(e)