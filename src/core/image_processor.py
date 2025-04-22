# src/core/image_processor.py
import os
from PIL import Image # Necesitarás: pip install Pillow
try:
    from pyzbar import pyzbar # Necesitarás: pip install pyzbar (y la librería ZBar instalada en el sistema)
except ImportError:
    print("Advertencia: pyzbar no encontrado. La lectura de códigos de barras no funcionará.")
    pyzbar = None

try:
    import pytesseract # Necesitarás: pip install pytesseract (y el motor Tesseract OCR instalado en el sistema)
    # Configura la ruta al ejecutable de Tesseract si no está en el PATH del sistema
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Ejemplo en Windows
except ImportError:
    print("Advertencia: pytesseract no encontrado. El OCR no funcionará.")
    pytesseract = None
except Exception as e: # Captura otros errores como Tesseract no encontrado
     print(f"Error al inicializar Pytesseract: {e}. El OCR no funcionará.")
     pytesseract = None


def extract_barcode(image_path: str) -> str | None:
    """Intenta leer un código de barras de la imagen."""
    if not pyzbar:
        print("pyzbar no está disponible.")
        return None
    try:
        img = Image.open(image_path)
        barcodes = pyzbar.decode(img)
        if barcodes:
            # Asumir que el primer código de barras encontrado es el bueno
            # Podrías necesitar lógica adicional si hay múltiples códigos
            barcode_data = barcodes[0].data.decode('utf-8')
            print(f"Código de barras encontrado: {barcode_data}")
            # Podrías validar si 'barcode_data' parece un número de guía válido
            return barcode_data
        else:
            print("No se encontraron códigos de barras.")
            return None
    except Exception as e:
        print(f"Error al procesar código de barras en {os.path.basename(image_path)}: {e}")
        return None


def extract_text_ocr(image_path: str) -> str | None:
    """Intenta extraer texto usando OCR y busca un patrón de número de guía."""
    if not pytesseract:
        print("Pytesseract no está disponible.")
        return None
    try:
        img = Image.open(image_path)
        # Preprocesamiento opcional (convertir a escala de grises, binarizar, etc.)
        # img = img.convert('L') # Escala de grises
        # ... otras técnicas de mejora de imagen ...

        # Extraer texto
        text = pytesseract.image_to_string(img, lang='spa') # Asume español, ajusta si es necesario
        print(f"Texto extraído por OCR:\n---\n{text}\n---")

        # --- Lógica para encontrar el número de guía en el texto ---
        # Esto es MUY dependiente del formato de tus guías.
        # Necesitarás expresiones regulares o lógica de búsqueda.
        # Ejemplo MUY BÁSICO (asume número de guía de 10 dígitos):
        import re
        # patron_guia = re.compile(r'\b\d{10,15}\b') # Busca números de 10 a 15 dígitos
        patron_guia = re.compile(r'\b770\d{10,}\b') # Ejemplo: Empieza con 770 y tiene al menos 10 dígitos más

        matches = patron_guia.findall(text)

        if matches:
            # Asumir que el primer match es el bueno, o el más largo, etc.
            numero_encontrado = matches[0]
            print(f"Número de guía encontrado por OCR: {numero_encontrado}")
            return numero_encontrado
        else:
            print("No se encontró un patrón de número de guía en el texto OCR.")
            return None

    except Exception as e:
        print(f"Error durante OCR en {os.path.basename(image_path)}: {e}")
        return None


def get_guide_number(image_path: str) -> str | None:
    """Función principal para obtener el número de guía. Intenta barcode y luego OCR."""
    print(f"Intentando obtener número de guía para: {os.path.basename(image_path)}")

    # 1. Intentar con Código de Barras
    numero_guia = extract_barcode(image_path)
    if numero_guia:
        print("Número obtenido por código de barras.")
        return numero_guia

    # 2. Si falla el código de barras, intentar con OCR
    print("Código de barras no encontrado o fallido, intentando OCR...")
    numero_guia = extract_text_ocr(image_path)
    if numero_guia:
        print("Número obtenido por OCR.")
        return numero_guia

    # 3. Si ambos fallan
    print("No se pudo obtener el número de guía por ningún método.")
    return None