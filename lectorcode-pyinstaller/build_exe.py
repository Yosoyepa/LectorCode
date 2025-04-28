#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import site
from pathlib import Path

def ensure_pyinstaller_installed():
    """Verifica que PyInstaller esté instalado, o lo instala si es necesario."""
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} ya está instalado")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller instalado correctamente")

def find_dll_in_venv(dll_name):
    """Busca un archivo DLL en el entorno virtual."""
    # Buscar en site-packages
    packages_dirs = site.getsitepackages()
    
    for dir_path in packages_dirs:
        # Buscar recursivamente
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.lower() == dll_name.lower():
                    return os.path.join(root, file)
    return None

def copy_dlls_to_directory(target_dir):
    """Copia las DLLs necesarias a un directorio temporal."""
    # Asegurar que el directorio destino existe
    os.makedirs(target_dir, exist_ok=True)
    
    # Lista de DLLs necesarias para pyzbar
    dlls = ['libiconv.dll', 'libzbar-64.dll', 'libzbar-0.dll', 'libzbar.dll']
    
    # Diccionario para almacenar las rutas encontradas
    found_dlls = {}
    
    # Buscar cada DLL
    for dll in dlls:
        dll_path = find_dll_in_venv(dll)
        if dll_path:
            print(f"Encontrada DLL: {dll} en {dll_path}")
            # Copiar al directorio temporal
            target_path = os.path.join(target_dir, dll)
            shutil.copy2(dll_path, target_path)
            found_dlls[dll] = target_path
        else:
            print(f"ADVERTENCIA: No se encontró la DLL {dll}")
    
    return found_dlls

def build_executable():
    """Ejecuta PyInstaller para crear el ejecutable"""
    # Ruta al directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    
    # Crear directorio temporal para DLLs
    dll_temp_dir = project_root / "temp_dlls"
    os.makedirs(dll_temp_dir, exist_ok=True)
    
    # Copiar DLLs necesarias
    print("Copiando DLLs necesarias...")
    found_dlls = copy_dlls_to_directory(dll_temp_dir)
    
    # Verificar qué directorios realmente existen
    ui_files_dir = project_root / "src" / "ui" / "ui_files"
    
    print(f"Verificando directorios de recursos:")
    print(f"  UI Files: {ui_files_dir} - {'Existe' if ui_files_dir.exists() else 'No existe'}")
    
    # Construir comando PyInstaller basado solo en los directorios existentes
    cmd = [
        "pyinstaller",
        "--name=LectorCode",
        "--windowed",  # Sin consola (GUI)
        "--clean",     # Limpiar caché
        "--noconfirm"  # No preguntar confirmación para sobreescribir
    ]
    
    # Agregar UI files si existen
    if ui_files_dir.exists():
        cmd.append(f"--add-data={ui_files_dir}{os.pathsep}src/ui/ui_files")
    
    # Agregar cada DLL encontrada
    for dll_name, dll_path in found_dlls.items():
        cmd.append(f"--add-binary={dll_path}{os.pathsep}.")
    
    # Agregar los DLLs descargados manualmente
    dll_dir = project_root / "dlls"
    if dll_dir.exists():
        for dll_file in dll_dir.glob("*.dll"):
            cmd.append(f"--add-binary={dll_file}{os.pathsep}.")
    
    # Agregar el script principal
    cmd.append(str(project_root / "main.py"))
    
    # Cambiar al directorio raíz del proyecto
    original_dir = os.getcwd()
    os.chdir(project_root)
    
    try:
        print(f"Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("\n¡Compilación exitosa!")
        print(f"El ejecutable se encuentra en: {project_root}/dist/LectorCode/")
    except subprocess.CalledProcessError as e:
        print(f"\nError durante la compilación: {e}")
    finally:
        # Volver al directorio original
        os.chdir(original_dir)
        
        # Limpiar directorio temporal
        try:
            shutil.rmtree(dll_temp_dir)
            print(f"Directorio temporal eliminado: {dll_temp_dir}")
        except Exception as e:
            print(f"No se pudo eliminar el directorio temporal: {e}")

if __name__ == "__main__":
    ensure_pyinstaller_installed()
    build_executable()