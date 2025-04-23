# src/core/image_processor.py
import os
import sys
# Importar librerías de procesamiento. Añadir manejo de errores por si no están instaladas.
try:
    from PIL import Image
except ImportError:
    print("Error Crítico: La librería Pillow no está instalada. Ejecuta: pip install Pillow")
    # Pillow es esencial para abrir imágenes, salir si no está.
    sys.exit("Error Crítico: Falta la librería Pillow.")

try:
    # Para códigos de barras
    from pyzbar import pyzbar
except ImportError:
    print("Advertencia: La librería pyzbar no está instalada (pip install pyzbar). "
          "La lectura de códigos de barras no funcionará. "
          "Además, requiere que la librería ZBar esté instalada en el sistema.")
    pyzbar = None # Establecer a None para poder verificar su disponibilidad

try:
    # Para OCR
    import pytesseract
except ImportError:
    print("Advertencia: La librería pytesseract no está instalada (pip install pytesseract). "
          "El OCR no funcionará. "
          "Además, requiere que el motor Tesseract OCR esté instalado en el sistema.")
    pytesseract = None # Establecer a None
    tessdata_config = '' # Definir variable para evitar errores posteriores
except Exception as e_tess_init:
     # Capturar otros errores, como Tesseract no encontrado en el PATH
     print(f"Error al inicializar Pytesseract: {e_tess_init}. El OCR podría no funcionar.")
     # Podría ser que pytesseract esté instalado pero Tesseract no.
     # No establecemos pytesseract a None aquí, pero el config será vacío.
     tessdata_config = ''


# --- Configuración de Rutas para PyInstaller ---
tessdata_config = '' # Inicializar config global
tesseract_cmd_path = None # Inicializar ruta al cmd

# Determinar si la aplicación está 'congelada' (empaquetada por PyInstaller)
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Estamos ejecutando desde el .exe empaquetado
    print("Modo congelado (ejecutable) detectado.")
    # _MEIPASS es la ruta al directorio temporal donde se desempaqueta todo (en modo --onefile)
    # o la ruta a la carpeta de la app (en modo --onedir)
    bundle_dir = sys._MEIPASS
    print(f"Directorio del bundle (_MEIPASS): {bundle_dir}")

    # --- Opción A: Configurar solo TESSDATA ---
    # Asume que tesseract.exe está en el PATH del sistema de destino o que
    # el usuario lo instalará por separado. Solo necesitamos decirle a
    # pytesseract dónde están nuestros datos de idioma empaquetados.
    # Asumimos que copiamos la carpeta 'tessdata' a la raíz del bundle.
    tessdata_dir_bundle = os.path.join(bundle_dir, 'tessdata')
    print(f"Buscando tessdata empaquetado en: {tessdata_dir_bundle}")

    if os.path.isdir(tessdata_dir_bundle):
        # Crear la opción de configuración para pytesseract
        tessdata_config = f'--tessdata-dir "{tessdata_dir_bundle}"'
        print(f"Configuración de TESSDATA para pytesseract: {tessdata_config}")
        # Opcionalmente, intentar establecer la variable de entorno (puede o no funcionar)
        # os.environ['TESSDATA_PREFIX'] = tessdata_dir_bundle
    else:
        print("ADVERTENCIA: Carpeta 'tessdata' no encontrada en el bundle. El OCR probablemente fallará.")
        # tessdata_config permanecerá vacío

    # --- Opción B: Especificar ruta a tesseract.exe (Si lo empaquetas también) ---
    # Esto requiere añadir tesseract.exe y sus DLLs al bundle con --add-binary o --add-data
    # tesseract_exe_bundle_path = os.path.join(bundle_dir, 'tesseract', 'tesseract.exe') # Ejemplo de ruta relativa
    # print(f"Buscando tesseract.exe empaquetado en: {tesseract_exe_bundle_path}")
    # if os.path.exists(tesseract_exe_bundle_path):
    #     if pytesseract: # Solo si pytesseract se importó correctamente
    #         pytesseract.pytesseract.tesseract_cmd = tesseract_exe_bundle_path
    #         tesseract_cmd_path = tesseract_exe_bundle_path # Guardar para posible uso futuro
    #         print(f"Ruta de tesseract_cmd establecida a: {tesseract_cmd_path}")
    # else:
    #     print("ADVERTENCIA: tesseract.exe no encontrado en el bundle (si se intentó empaquetar).")

elif pytesseract:
    # No estamos congelados (ejecutando .py directamente)
    print("Modo script Python detectado.")
    # Opcional: Especificar ruta a tesseract.exe si no está en el PATH del sistema
    # (Ajusta esta ruta según tu instalación local)
    # try:
    #     tesseract_install_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Ejemplo Windows
    #     if os.path.exists(tesseract_install_path):
    #          pytesseract.pytesseract.tesseract_cmd = tesseract_install_path
    #          print(f"Establecida ruta local de tesseract: {tesseract_install_path}")
    #     else:
    #          print(f"Tesseract no encontrado en ruta local especificada: {tesseract_install_path}, se usará PATH.")
    # except Exception as e:
    #      print(f"Error al intentar establecer ruta local de Tesseract: {e}")
    # tessdata_config sigue vacío, usará la configuración por defecto de Tesseract


# ==========================================
# ===== Funciones de Procesamiento =====
# ==========================================

def extract_barcode(image_path: str) -> str | None:
    """
    Intenta leer un código de barras desde un archivo de imagen.

    Args:
        image_path: Ruta completa al archivo de imagen.

    Returns:
        El contenido del primer código de barras encontrado (como string),
        o None si no se encuentra o hay un error.
    """
    if not pyzbar:
        print("Intento de usar extract_barcode, pero pyzbar no está disponible.")
        return None # Salir si la librería no se cargó

    try:
        print(f"Intentando leer código de barras de: {os.path.basename(image_path)}")
        # Abrir la imagen usando Pillow
        img = Image.open(image_path)
        # Decodificar códigos de barras en la imagen
        barcodes = pyzbar.decode(img)

        if barcodes:
            # Tomar el primer código de barras encontrado
            barcode_data = barcodes[0].data
            # Decodificar bytes a string (usualmente utf-8)
            barcode_string = barcode_data.decode('utf-8')
            print(f"  Código de barras encontrado: {barcode_string}")
            # Podrías añadir validaciones aquí si esperas un formato específico
            return barcode_string
        else:
            print("  No se encontraron códigos de barras.")
            return None # No se encontraron códigos
    except FileNotFoundError:
         print(f"Error en extract_barcode: Archivo no encontrado - {image_path}")
         return None
    except Exception as e:
        # Capturar otros errores (ej. Pillow no puede abrir la imagen, error en ZBar)
        print(f"Error inesperado en extract_barcode para {os.path.basename(image_path)}: {e}")
        # import traceback; traceback.print_exc() # Descomentar para ver stacktrace completo
        return None


def extract_text_ocr(image_path: str) -> str | None:
    """
    Intenta extraer texto de una imagen usando Tesseract OCR y busca un
    patrón específico que corresponda a un número de guía.

    Args:
        image_path: Ruta completa al archivo de imagen.

    Returns:
        El número de guía encontrado (como string) que coincida con el patrón,
        o None si no se encuentra, Tesseract no está disponible, o hay un error.
    """
    global tessdata_config # Usar la configuración global (importante para .exe)

    if not pytesseract:
        print("Intento de usar extract_text_ocr, pero pytesseract no está disponible.")
        return None # Salir si la librería no se cargó o no se inicializó bien

    try:
        print(f"Intentando OCR en: {os.path.basename(image_path)}")
        # Abrir la imagen
        img = Image.open(image_path)

        # --- Preprocesamiento de Imagen (Opcional pero a menudo útil) ---
        # Convertir a escala de grises podría ayudar
        # img = img.convert('L')
        # Aplicar umbral (binarización) podría ayudar
        # threshold = 180
        # img = img.point(lambda p: p > threshold and 255)
        # Considerar librerías como OpenCV (cv2) para preprocesamiento más avanzado si es necesario

        # --- Ejecutar Tesseract OCR ---
        # lang='spa' para español. Ajusta según el idioma de tus guías.
        # Pasar la configuración de tessdata si se definió.
        print(f"  Ejecutando image_to_string con config: '{tessdata_config}'")
        text = pytesseract.image_to_string(img, lang='spa', config=tessdata_config)

        # Imprimir texto extraído para depuración (puede ser mucho)
        # print(f"  Texto extraído por OCR:\n---\n{text}\n---") # Descomentar si necesitas ver todo

        # --- Buscar el Número de Guía en el Texto ---
        # Esta es la parte que MÁS necesita adaptarse a TUS guías.
        # Usar Expresiones Regulares (regex) es lo más común.
        import re

        # Ejemplo 1: Buscar un número que empiece con "770" seguido de 10 o más dígitos.
        patron_guia = re.compile(r'\b(770\d{10,})\b')

        # Ejemplo 2: Buscar un número de exactamente 12 dígitos.
        # patron_guia = re.compile(r'\b(\d{12})\b')

        # Ejemplo 3: Buscar un número de 10 a 15 dígitos cerca de la palabra "GUIA".
        # Podrías buscar la palabra y luego buscar números cerca, o usar patrones más complejos.
        # patron_guia = re.compile(r'GUIA\s*[:\-]?\s*(\d{10,15})\b', re.IGNORECASE) # Ignora mayúsculas/minúsculas

        matches = patron_guia.findall(text) # findall devuelve todas las coincidencias

        if matches:
            # Si encuentra una o más coincidencias, ¿cuál tomar?
            # Por simplicidad, tomaremos la primera encontrada.
            # Podrías necesitar lógica más compleja (ej. la más larga, la que esté en cierta zona).
            numero_encontrado = matches[0]
             # A veces OCR añade espacios o caracteres raros, limpiar un poco
            numero_encontrado_limpio = "".join(filter(str.isalnum, numero_encontrado))
            print(f"  Patrón de número de guía encontrado: {numero_encontrado_limpio}")
            return numero_encontrado_limpio
        else:
            print("  No se encontró un patrón de número de guía en el texto OCR.")
            return None # No se encontró el patrón

    except FileNotFoundError:
         print(f"Error en extract_text_ocr: Archivo no encontrado - {image_path}")
         return None
    except pytesseract.TesseractNotFoundError:
        print("Error Crítico en extract_text_ocr: No se encontró el ejecutable de Tesseract OCR. "
              "Asegúrate de que esté instalado y en el PATH del sistema, o configura la ruta en el código.")
        # Podrías lanzar una excepción aquí o mostrar un mensaje al usuario la primera vez.
        return None # Indicar fallo
    except Exception as e:
        print(f"Error inesperado durante OCR en {os.path.basename(image_path)}: {e}")
        # import traceback; traceback.print_exc() # Descomentar para ver stacktrace completo
        return None


def get_guide_number(image_path: str) -> str | None:
    """
    Función principal para obtener el número de guía de una imagen.
    Intenta primero con código de barras y, si falla, intenta con OCR.

    Args:
        image_path: Ruta completa al archivo de imagen.

    Returns:
        El número de guía encontrado (string) o None si ambos métodos fallan.
    """
    print(f"Obteniendo número de guía para: {os.path.basename(image_path)}")

    # 1. Intentar leer Código de Barras
    if pyzbar: # Solo intentar si la librería está disponible
        numero_guia_bc = extract_barcode(image_path)
        if numero_guia_bc:
            print("--> Número obtenido por Código de Barras.")
            return numero_guia_bc
        else:
            print("  Código de barras no encontrado o ilegible.")
    else:
        print("  Librería pyzbar no disponible, saltando lectura de código de barras.")

    # 2. Si falla el código de barras (o no está disponible), intentar OCR
    if pytesseract: # Solo intentar si la librería está disponible
        print("  Intentando con OCR...")
        numero_guia_ocr = extract_text_ocr(image_path)
        if numero_guia_ocr:
            print("--> Número obtenido por OCR.")
            return numero_guia_ocr
        else:
            print("  OCR falló o no encontró el patrón.")
    else:
        print("  Librería pytesseract no disponible, saltando OCR.")

    # 3. Si ambos métodos fallan o no están disponibles
    print("==> No se pudo obtener el número de guía por ningún método.")
    return None

# --- Fin del archivo src/core/image_processor.py ---