# src/core/image_processor.py
import os
import sys
# Importar librerías de procesamiento. Añadir manejo de errores por si no están instaladas.
try:
    from PIL import Image
except ImportError:
    print("Error Crítico: La librería Pillow no está instalada. Ejecuta: pip install Pillow")
    sys.exit("Error Crítico: Falta la librería Pillow.")

try:
    # Para códigos de barras
    from pyzbar import pyzbar
except ImportError:
    print("Advertencia: La librería pyzbar no está instalada (pip install pyzbar). "
          "La lectura de códigos de barras no funcionará. "
          "Además, requiere que la librería ZBar esté instalada (o sus DLLs incluidas).")
    pyzbar = None # Establecer a None para poder verificar su disponibilidad

try:
    # Para OCR
    import pytesseract
except ImportError:
    print("Advertencia: La librería pytesseract no está instalada (pip install pytesseract). "
          "El OCR no funcionará. "
          "Además, requiere que el motor Tesseract OCR esté instalado (o incluido).")
    pytesseract = None
    tessdata_config = ''
except Exception as e_tess_init:
     print(f"Error al inicializar Pytesseract: {e_tess_init}. El OCR podría no funcionar.")
     tessdata_config = ''


# --- Configuración de Rutas para PyInstaller ---
tessdata_config = '' # Inicializar config global para tessdata
# No necesitamos tesseract_cmd_path global si lo establecemos directamente abajo

# Determinar si la aplicación está 'congelada' (empaquetada por PyInstaller)
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Estamos ejecutando desde el .exe empaquetado
    print("Modo congelado (ejecutable) detectado.")
    # _MEIPASS es la ruta al directorio temporal (modo --onefile)
    # o la ruta a la carpeta de la app (modo --onedir)
    bundle_dir = sys._MEIPASS
    print(f"Directorio del bundle (_MEIPASS): {bundle_dir}")

    # --- Configurar TESSDATA ---
    # Asume que 'tessdata' se copia a la raíz del bundle con --add-data "...;tessdata"
    tessdata_dir_bundle = os.path.join(bundle_dir, 'tessdata')
    print(f"Buscando tessdata empaquetado en: {tessdata_dir_bundle}")

    if os.path.isdir(tessdata_dir_bundle):
        # Crear la opción de configuración para pytesseract
        tessdata_config = f'--tessdata-dir "{tessdata_dir_bundle}"'
        print(f"Configuración de TESSDATA para pytesseract: {tessdata_config}")
    else:
        print("ADVERTENCIA CRÍTICA: Carpeta 'tessdata' no encontrada en el bundle. El OCR fallará.")
        # Considerar mostrar error al usuario o desactivar OCR en la app principal

    # --- Configurar RUTA A TESSERACT.EXE (Opción B - ACTIVADA) ---
    # Asume que la carpeta de Tesseract se copia a una subcarpeta 'tesseract' en el bundle
    # usando --add-data "C:/Program Files/Tesseract-OCR;tesseract"
    tesseract_exe_bundle_path = os.path.join(bundle_dir, 'tesseract', 'tesseract.exe')
    print(f"Buscando tesseract.exe empaquetado en: {tesseract_exe_bundle_path}")

    # ===> ESTA ES LA PARTE MODIFICADA Y ACTIVADA <===
    if os.path.exists(tesseract_exe_bundle_path):
        if pytesseract: # Solo si pytesseract se importó correctamente
            # Establecer la ruta al ejecutable que pytesseract debe usar
            pytesseract.pytesseract.tesseract_cmd = tesseract_exe_bundle_path
            print(f"Ruta de tesseract_cmd establecida a (empaquetado): {tesseract_exe_bundle_path}")
    else:
        # Si no se encuentra el ejecutable empaquetado, el OCR no funcionará.
        print(f"ERROR CRÍTICO: tesseract.exe no encontrado en {tesseract_exe_bundle_path}. "
              "Asegúrate de incluirlo correctamente con --add-data 'RUTA/TESSERACT;tesseract'. El OCR no funcionará.")
        # Podrías establecer pytesseract a None aquí para desactivarlo completamente si falla
        # pytesseract = None
    # ===> FIN DE LA PARTE MODIFICADA Y ACTIVADA <===

elif pytesseract:
    # Modo Script Python (ejecutando .py directamente)
    print("Modo script Python detectado.")
    # Aquí puedes mantener tu configuración local si es necesaria (opcional)
    # tesseract_local_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # if os.path.exists(tesseract_local_path):
    #     pytesseract.pytesseract.tesseract_cmd = tesseract_local_path
    #     print(f"Establecida ruta local de tesseract: {tesseract_local_path}")
    # else:
    #     print(f"Tesseract no encontrado en ruta local: {tesseract_local_path}. Usando PATH.")
    # tessdata_config sigue vacío, usará la configuración por defecto de Tesseract

# ==========================================
# ===== Funciones de Procesamiento =====
# ==========================================

def extract_barcode(image_path: str) -> str | None:
    """Intenta leer un código de barras desde un archivo de imagen."""
    if not pyzbar:
        print("Intento de usar extract_barcode, pero pyzbar no está disponible.")
        return None
    try:
        print(f"Intentando leer código de barras de: {os.path.basename(image_path)}")
        img = Image.open(image_path)
        barcodes = pyzbar.decode(img)
        if barcodes:
            barcode_data = barcodes[0].data
            barcode_string = barcode_data.decode('utf-8')
            print(f"  Código de barras encontrado: {barcode_string}")
            return barcode_string
        else:
            print("  No se encontraron códigos de barras.")
            return None
    except FileNotFoundError:
         print(f"Error en extract_barcode: Archivo no encontrado - {image_path}")
         return None
    except Exception as e:
        print(f"Error inesperado en extract_barcode para {os.path.basename(image_path)}: {e}")
        return None


def extract_text_ocr(image_path: str) -> str | None:
    """Intenta extraer texto usando Tesseract OCR."""
    global tessdata_config # Usar la configuración global para tessdata

    if not pytesseract:
        print("Intento de usar extract_text_ocr, pero pytesseract no está disponible.")
        return None

    # Verificar si el comando tesseract se pudo establecer (útil para debug)
    tesseract_command = getattr(pytesseract.pytesseract, 'tesseract_cmd', 'No establecido (usará PATH)')
    print(f"  Usando tesseract_cmd: {tesseract_command}")

    try:
        print(f"Intentando OCR en: {os.path.basename(image_path)}")
        img = Image.open(image_path)

        # --- Ejecutar Tesseract OCR ---
        print(f"  Ejecutando image_to_string con config: '{tessdata_config}'")
        # La ruta a tesseract.exe la toma de pytesseract.tesseract_cmd si fue establecida
        text = pytesseract.image_to_string(img, lang='spa', config=tessdata_config)

        # --- Buscar el Número de Guía en el Texto ---
        import re
        # AJUSTA ESTE PATRÓN SEGÚN TUS GUÍAS
        patron_guia = re.compile(r'\b(770\d{10,})\b')
        matches = patron_guia.findall(text)

        if matches:
            numero_encontrado = matches[0]
            numero_encontrado_limpio = "".join(filter(str.isalnum, numero_encontrado))
            print(f"  Patrón de número de guía encontrado: {numero_encontrado_limpio}")
            return numero_encontrado_limpio
        else:
            print("  No se encontró un patrón de número de guía en el texto OCR.")
            return None

    except FileNotFoundError:
         print(f"Error en extract_text_ocr: Archivo no encontrado - {image_path}")
         return None
    except pytesseract.TesseractNotFoundError as tess_error:
        # Este error es común si tesseract_cmd no es correcto o tesseract no está accesible
        print(f"Error Crítico en extract_text_ocr: TesseractNotFoundError - {tess_error}. "
              f"Verifica la ruta establecida para tesseract_cmd ('{tesseract_command}') y "
              "asegúrate que el ejecutable y sus dependencias fueron incluidos correctamente.")
        return None
    except Exception as e:
        # Capturar otros errores inesperados durante el OCR
        print(f"Error inesperado durante OCR en {os.path.basename(image_path)}: {e}")
        # import traceback; traceback.print_exc() # Útil para depuración avanzada
        return None


def get_guide_number(image_path: str) -> str | None:
    """Función principal: Intenta barcode y luego OCR."""
    print(f"Obteniendo número de guía para: {os.path.basename(image_path)}")

    # 1. Intentar Código de Barras
    if pyzbar:
        numero_guia_bc = extract_barcode(image_path)
        if numero_guia_bc:
            print("--> Número obtenido por Código de Barras.")
            return numero_guia_bc
        else:
            print("  Código de barras no encontrado o ilegible.")
    else:
        print("  Librería pyzbar no disponible.")

    # 2. Intentar OCR
    if pytesseract:
        print("  Intentando con OCR...")
        numero_guia_ocr = extract_text_ocr(image_path)
        if numero_guia_ocr:
            print("--> Número obtenido por OCR.")
            return numero_guia_ocr
        else:
            print("  OCR falló o no encontró el patrón.")
    else:
        print("  Librería pytesseract no disponible.")

    print("==> No se pudo obtener el número de guía por ningún método.")
    return None

# --- Fin del archivo src/core/image_processor.py ---