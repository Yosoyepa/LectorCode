# src/core/processing_handler.py
import os
from . import image_processor  # Importar desde el mismo paquete core
from . import file_operations

def process_single_file_auto(current_path: str) -> dict:
    """
    Orquesta el procesamiento automático de un solo archivo.
    1. Extrae el número de guía (Barcode/OCR).
    2. Determina el nuevo nombre.
    3. Intenta renombrar el archivo.
    4. Devuelve un diccionario con el resultado detallado.

    Args:
        current_path: La ruta completa actual del archivo a procesar.

    Returns:
        Un diccionario indicando el estado y detalles, ej:
        {"status": "success", "new_name": "...", "new_path": "..."}
        {"status": "no_rename_needed", "current_name": "..."}
        {"status": "ocr_failed", "message": "...", "current_name": "..."}
        {"status": "rename_failed", "message": "...", "current_name": "..."}
        {"status": "target_exists", "message": "...", "current_name": "...", "target_name": "..."}
        {"status": "error", "message": "...", "current_name": "..."} # Errores generales
    """
    current_name = os.path.basename(current_path)
    print(f"[Handler] Procesando automáticamente: {current_name}")

    if not os.path.exists(current_path):
        return {"status": "error", "message": f"Archivo no encontrado en {current_path}", "current_name": current_name}

    # 1. Extraer número de guía
    numero_guia = None
    try:
        numero_guia = image_processor.get_guide_number(current_path)
    except Exception as e:
        print(f"[Handler] Error en image_processor: {e}")
        return {"status": "ocr_failed", "message": f"Error durante OCR/BC: {e}", "current_name": current_name}

    if not numero_guia:
        return {"status": "ocr_failed", "message": "No se pudo extraer número de guía.", "current_name": current_name}

    numero_guia_limpio = "".join(filter(str.isalnum, str(numero_guia)))
    if not numero_guia_limpio:
        return {"status": "ocr_failed", "message": f"Número de guía inválido '{numero_guia}'.", "current_name": current_name}

    # 2. Determinar nuevo nombre/ruta
    directorio = os.path.dirname(current_path)
    _, extension = os.path.splitext(current_name)
    nuevo_nombre = f"{numero_guia_limpio}{extension}"
    nueva_ruta = os.path.join(directorio, nuevo_nombre)
    nueva_ruta_norm = os.path.normpath(nueva_ruta)
    ruta_original_norm = os.path.normpath(current_path)

    # 3. Verificar si se necesita renombrar
    if nuevo_nombre == current_name or nueva_ruta_norm == ruta_original_norm:
         print(f"[Handler] El archivo '{current_name}' ya tiene el nombre correcto.")
         # Devolver éxito pero indicando que no hubo cambio efectivo
         return {"status": "no_rename_needed", "current_name": current_name, "new_path": nueva_ruta}

    # 4. Verificar si el destino ya existe
    if os.path.exists(nueva_ruta_norm):
        print(f"[Handler] Conflicto: El destino '{nuevo_nombre}' ya existe.")
        return {"status": "target_exists", "message": f"El destino '{nuevo_nombre}' ya existe.", "current_name": current_name, "target_name": nuevo_nombre}

    # 5. Intentar renombrar
    print(f"[Handler] Intentando renombrar: '{current_path}' -> '{nueva_ruta}'")
    exito, mensaje_error = file_operations.rename_scan(current_path, nueva_ruta)

    if exito:
        print(f"[Handler] Renombrado con éxito a '{nuevo_nombre}'.")
        return {"status": "success", "new_name": nuevo_nombre, "new_path": nueva_ruta}
    else:
        print(f"[Handler] Fallo al renombrar: {mensaje_error}")
        return {"status": "rename_failed", "message": f"Error al renombrar: {mensaje_error}", "current_name": current_name}


def rename_single_file_manual(current_path: str, current_name: str, new_base_name: str) -> dict:
    """
    Orquesta el renombrado manual de un solo archivo.
    1. Valida el nuevo nombre base.
    2. Construye la nueva ruta.
    3. Verifica conflictos.
    4. Intenta renombrar.
    5. Devuelve un diccionario con el resultado.

    Args:
        current_path: Ruta completa actual del archivo.
        current_name: Nombre actual del archivo (como se muestra en UI).
        new_base_name: Nuevo nombre base (sin extensión) ingresado por el usuario.

    Returns:
        Diccionario de resultado similar a process_single_file_auto.
    """
    print(f"[Handler] Procesando manualmente: {current_name} -> {new_base_name}")

    # 1. Validar nuevo nombre base (podría moverse a utils si se reutiliza)
    if not new_base_name:
         return {"status": "error", "message": "El nuevo nombre no puede estar vacío.", "current_name": current_name}
    invalid_chars_pattern = r'[\<\>\:\"\/\\\|\?\*]'
    import re
    if re.search(invalid_chars_pattern, new_base_name):
         return {"status": "error", "message": f"El nombre '{new_base_name}' contiene caracteres inválidos.", "current_name": current_name}

    # 2. Construir nueva ruta
    if not os.path.exists(current_path):
        return {"status": "error", "message": f"Archivo original no encontrado en {current_path}", "current_name": current_name}

    _, extension = os.path.splitext(current_name) # Usar extensión del nombre actual del item
    nuevo_nombre_completo = f"{new_base_name}{extension}"
    directorio = os.path.dirname(current_path)
    nueva_ruta = os.path.join(directorio, nuevo_nombre_completo)
    nueva_ruta_norm = os.path.normpath(nueva_ruta)
    ruta_original_norm = os.path.normpath(current_path)

    # 3. Verificar si se necesita renombrar
    if nuevo_nombre_completo == current_name or nueva_ruta_norm == ruta_original_norm:
        return {"status": "no_rename_needed", "message": "El nombre ingresado es el mismo que el actual.", "current_name": current_name}

    # 4. Verificar conflicto
    if os.path.exists(nueva_ruta_norm):
        return {"status": "target_exists", "message": f"Ya existe un archivo llamado '{nuevo_nombre_completo}'.", "current_name": current_name, "target_name": nuevo_nombre_completo}

    # 5. Intentar renombrar
    print(f"[Handler] Intentando renombrar manualmente: '{current_path}' -> '{nueva_ruta}'")
    exito, mensaje_error = file_operations.rename_scan(current_path, nueva_ruta)

    if exito:
        print(f"[Handler] Renombrado manual exitoso a '{nuevo_nombre_completo}'.")
        return {"status": "success", "new_name": nuevo_nombre_completo, "new_path": nueva_ruta}
    else:
        print(f"[Handler] Fallo en renombrado manual: {mensaje_error}")
        return {"status": "rename_failed", "message": f"Error al renombrar: {mensaje_error}", "current_name": current_name}