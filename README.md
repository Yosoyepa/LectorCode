# LectorCode

![Logo LectorCode](src/ui/iconos/logo_madre.png)

## Descripción

LectorCode es una aplicación desktop desarrollada en Python que facilita el procesamiento y renombrado de imágenes escaneadas de guías de envío. La aplicación permite:

- Cargar imágenes escaneadas de guías (.jpg, .png, .tif, etc.)
- Reconocer automáticamente números de guía mediante:
  - Lectura de códigos de barras
  - Reconocimiento óptico de caracteres (OCR)
- Renombrar archivos de forma automática o manual
- Gestionar lotes de archivos simultáneamente
- Previsualizar las imágenes mientras se procesan

## Características

- **Interfaz gráfica intuitiva**: Diseñada con PyQt5 para facilitar el manejo de múltiples archivos
- **Procesamiento dual**: Combina lectura de códigos de barras (pyzbar) y OCR (Tesseract)
- **Edición manual**: Permite editar manualmente los nombres cuando el reconocimiento automático falla
- **Procesamiento por lotes**: Procesa múltiples archivos con un solo clic
- **Navegación sencilla**: Facilita ver y editar archivos con botones de navegación
- **Multiplataforma**: Compatible con Windows, Linux y macOS (requiere instalación de dependencias específicas)

## Requisitos

### Requisitos de sistema
- Python 3.10 o superior
- 2GB de RAM mínimo
- Espacio en disco: 200MB mínimo

### Dependencias principales
- PyQt5: Interfaz gráfica
- Pillow: Procesamiento de imágenes
- pytesseract: OCR para reconocimiento de texto
- pyzbar: Lectura de códigos de barras
- Tesseract OCR: Motor de reconocimiento óptico (debe estar instalado a nivel de sistema)

## Instalación

### Opción 1: Desde el código fuente
1. Clona el repositorio:
   ```
   git clone https://github.com/usuario/LectorCode.git
   cd LectorCode
   ```

2. Crea un entorno virtual (recomendado):
   ```
   python -m venv venv
   # Activar en Windows
   venv\Scripts\activate
   # Activar en Linux/Mac
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Instala Tesseract OCR:
   - Windows: [Tesseract-OCR para Windows](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt install tesseract-ocr`
   - macOS: `brew install tesseract`

5. Ejecuta la aplicación:
   ```
   python main.py
   ```

## Uso

1. **Iniciar la aplicación**: Ejecuta LectorCode desde el acceso directo o mediante el comando `python main.py`.

2. **Cargar imágenes**: Haz clic en "Cargar" para seleccionar las imágenes escaneadas que deseas procesar.

3. **Seleccionar archivos**: Marca las casillas de los archivos que deseas procesar.

4. **Procesar automáticamente**: Haz clic en "Procesar" para iniciar el reconocimiento automático.

5. **Edición manual** (si es necesario):
   - Selecciona un archivo en la lista
   - Edita el nombre en el campo de texto
   - Haz clic en "Guardar" para renombrar manualmente

6. **Navegación**: Usa los botones "Anterior" y "Siguiente" para navegar entre las imágenes.

## Creación del ejecutable

Para crear un archivo ejecutable (.exe) de la aplicación:

1. Asegúrate de tener PyInstaller instalado:
   ```
   pip install pyinstaller
   ```

2. Ejecuta el script de compilación:
   ```
   python lectorcode-pyinstaller/build_exe.py
   ```

3. El ejecutable se generará en la carpeta LectorCode.

## Solución de problemas

### Problemas con el reconocimiento OCR
- Asegúrate de que Tesseract OCR esté correctamente instalado y en el PATH del sistema
- Verifica que las imágenes tengan suficiente resolución y contraste
- Ajusta el patrón de reconocimiento en image_processor.py si es necesario

### Problemas con la lectura de códigos de barras
- Asegúrate de que las DLLs de ZBar estén disponibles (normalmente se instalan con pyzbar)
- Las imágenes deben tener buena resolución y códigos de barras visibles

### El ejecutable no funciona
- Verifica que todas las DLLs necesarias estén incluidas (libiconv.dll, libzbar.dll)
- Asegúrate de incluir los archivos de Tesseract necesarios al crear el ejecutable

## Estructura del proyecto

```
LectorCode/
├── main.py                     # Punto de entrada principal
├── src/                        # Código fuente
│   ├── core/                   # Lógica de negocio
│   │   ├── file_operations.py  # Operaciones con archivos
│   │   ├── image_processor.py  # Procesamiento de imágenes, OCR, códigos de barras
│   │   └── processing_handler.py # Coordinación de procesamiento
│   ├── ui/                     # Interfaz de usuario
│   │   ├── components/         # Componentes reutilizables
│   │   ├── controllers/        # Controladores de UI
│   │   ├── ui_files/           # Archivos .ui de Qt Designer
│   │   ├── main_window.py      # Ventana principal
│   │   └── resources_rc.py     # Recursos compilados (iconos)
│   └── utils/                  # Utilidades
│       ├── file_helpers.py     # Helpers para archivos
│       ├── message_helpers.py  # Helpers para mensajes
│       └── ui_helpers.py       # Helpers para UI
└── lectorcode-pyinstaller/     # Scripts para crear ejecutable
    └── build_exe.py            # Script principal de compilación
```

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. Ver archivo `LICENSE` para más detalles.

## Contribuir

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Contacto

Juan Carlos Andrade - [andradeunigarrojuancarlos@gmmail.com](mailto:andradeunigarrojuancarlos@gmail.com)

Repositorio: [https://github.com/usuario/LectorCode](https://github.com/usuario/LectorCode)

---

Desarrollado por Juan Andrade © 2025