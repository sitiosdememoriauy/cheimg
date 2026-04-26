import subprocess
import shutil
import os
import platform
import sys

print("Iniciando compilación de Che IMG usando PyInstaller...")

# --- Chequeo de dependencias de empaquetado ---
try:
    import PyInstaller
except ImportError:
    print("\n❌ Error: No se encontró PyInstaller.")
    print("Asegúrate de instalarlo ejecutando: pip install pyinstaller")
    sys.exit(1)
# ----------------------------------------------

# 1. Ejecutamos PyInstaller
print("\nEmpaquetando motor de visión e interfaz (Esto puede tardar unos minutos)...")

# PyInstaller usa ";" en Windows y ":" en Linux/Mac para separar origen de destino
separador = ";" if platform.system() == "Windows" else ":"

comando_pyinstaller = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",           # Sobrescribir la carpeta dist/ sin preguntar
    "--onedir",              # Crear una carpeta contenedora (como en Che PDF)
    "--windowed",            # Ocultar la consola de fondo (es una app gráfica)
    "--name", "Che IMG",
    "--icon", "_internal/assets/icono_cheimg.ico",
    
    # --- INYECCIÓN DE ASSETS ---
    # Le decimos a PyInstaller que guarde los iconos exactamente en la misma ruta
    f"--add-data", f"_internal/assets{separador}_internal/assets",
    
    # --- RECOLECCIÓN DE CUSTOMTKINTER ---
    # CustomTkinter requiere que sus temas y fuentes se empaqueten explícitamente
    "--collect-all", "customtkinter",

    "--hidden-import", "PIL._tkinter_finder",

    "app.py"
]

try:
    subprocess.run(comando_pyinstaller, check=True)
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error crítico al compilar con PyInstaller. Revisa la consola arriba. Código: {e.returncode}")
    exit(1)

print("\nEnsamblando la distribución final...")

# ==============================================================
# CREAR UNA CARPETA CONTENEDORA LIMPIA
# ==============================================================
nombre_carpeta_cruda = "Che IMG"
ruta_generada = os.path.join('dist', nombre_carpeta_cruda)
ruta_dist_final = os.path.join('dist', 'Che_IMG')

# Limpiamos si ya existía de un intento anterior
if os.path.exists(ruta_dist_final):
    shutil.rmtree(ruta_dist_final)

# 2. Renombramos la carpeta para que quede igual de prolija que en el otro proyecto
if os.path.exists(ruta_generada):
    shutil.move(ruta_generada, ruta_dist_final)
else:
    print(f"⚠️ No se encontró la carpeta {ruta_generada}. Algo falló en la compilación.")
    exit(1)

# 3. Copiamos TODOS los archivos README dinámicamente
print(" -> Buscando archivos de documentación (README)...")
archivos_en_raiz = os.listdir('.')
for archivo in archivos_en_raiz:
    if archivo.lower().startswith('readme') and archivo.lower().endswith('.md'):
        print(f"    - Copiando {archivo}...")
        shutil.copy(archivo, ruta_dist_final)

# 4. Verificación de seguridad de los recursos gráficos
# PyInstaller debería haberlos copiado por el --add-data, pero confirmamos por si acaso.
ruta_assets_destino = os.path.join(ruta_dist_final, '_internal', 'assets')

if not os.path.exists(ruta_assets_destino):
    print(" -> Recuperando recursos visuales...")
    if os.path.exists(os.path.join('_internal', 'assets')):
        shutil.copytree(os.path.join('_internal', 'assets'), ruta_assets_destino, dirs_exist_ok=True)
else:
    print(" -> Recursos visuales integrados correctamente.")

print("\n=======================================================")
print("¡Éxito! El programa está listo y ensamblado.")
print("Puedes encontrar tu versión final en: 'dist/Che_IMG'")
print("=======================================================\n")
