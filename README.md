*Read this in [English](README-en.md).*

# 🖼️ Che IMG

**Che IMG** es un motor avanzado de reconstrucción documental mediante visión artificial. Está diseñado específicamente para unir y fusionar recortes escaneados de diarios, documentos históricos de gran tamaño y afiches que debieron ser digitalizados en partes debido a su tamaño, generando un único panorama en alta resolución.

Esta aplicación fue desarrollada por **sitiosdememoria.uy** con el objetivo de facilitar el análisis y la investigación de grandes volúmenes documentales. Cuenta con una licencia de software libre que permite su uso, estudio, difusión y modificación, como parte del compromiso del proyecto con las luchas por memoria, verdad y justicia.

## ✨ Características Principales

* **Unión Automática (SIFT):** Utiliza algoritmos de visión por computadora para detectar puntos clave (Keypoints) en las zonas de solapamiento de ambas imágenes, calculando y ejecutando la unión de forma automática.
* **Unión Manual por Puntos:** Para documentos complejos, muy dañados o con poco solapamiento, permite al usuario marcar manualmente puntos de control homólogos para forzar el cálculo de la perspectiva.
* **Fusión Inteligente (Feathering):** Aplica un algoritmo de fundido en la intersección de las imágenes, calculando distancias y opacidades (Alpha blending) para que la línea de corte sea invisible en el resultado final.
* **Conservación de Metadatos:** Al guardar la imagen final, el sistema recupera e inyecta los metadatos de las imágenes originales, conservando la densidad de píxeles (DPI), perfiles de color (ICC) y replicando las tablas de cuantización (calidad original) para evitar pérdida de fidelidad histórica.
* **Interfaz Gráfica (GUI) Amigable:** Construida en Python con CustomTkinter, ofreciendo un entorno oscuro, moderno y un lienzo interactivo con zoom, paneo y rotación para manipular los escaneos con facilidad.

## 🛠️ Requisitos del Sistema y Tecnologías

El código fuente está escrito en **Python 3**. Las dependencias principales son:
* `customtkinter` para la interfaz gráfica moderna.
* `opencv-python` (cv2) para el motor matemático, análisis SIFT y algoritmos RANSAC.
* `numpy` para el procesamiento matricial avanzado de las imágenes.
* `Pillow` (PIL) para la manipulación general de formatos de imagen, color y metadatos.

## 🚀 Instalación y Ejecución desde el Código Fuente

Si deseas ejecutar el programa desde su código fuente o contribuir a su desarrollo:

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/sitiosdememoriauy/cheimg/

2. **Crea y activa un entorno virtual:**
   
   **En Windows:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **En Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   cd cheimg
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación:**
   
   **En Windows:**
   ```bash
   python app.py
   ```
   
   **En Linux:**
   ```bash
   python3 app.py
   ```

## 📦 Compilación

Para distribuir el programa a usuarios finales de Windows o Linux sin que necesiten instalar Python, puedes compilarlo usando el empaquetador de Flet. Ejecuta el siguiente comando en la raíz del proyecto:

   **En Windows:**
   ```bash
   python compilar.py
   ```

   **En Linux:**
   ```bash
   python3 compilar.py
   ```

Esto generará una carpeta dist que contiene el ejecutable final y la carpeta de recursos. Puedes comprimir esa carpeta en un archivo .zip o .tar.gz para distribuirla.

## 📖 Guía de Uso Básica

1. Carga de Imágenes: Haz clic en los espacios "+" del lienzo principal para cargar la mitad izquierda y la mitad derecha del documento escaneado.
2. Método Automático: Presiona ✨ Unión Automática (SIFT). El programa escaneará las imágenes, buscará coincidencias y generará el panorama.
3. Método Manual: Si el escaneo es complejo, usa la rueda del ratón para hacer zoom, mantén presionado el clic para moverte y haz clic rápido para marcar al menos 4 puntos que coincidan exactamente en ambas imágenes (ej: una letra cortada, una mancha). Luego presiona 📌 Unión Manual (Puntos).
4. Edición: Puedes usar los botones inferiores para rotar las imágenes o eliminar puntos mal colocados con el clic derecho.
5. Exportación: Una vez procesada la unión, se abrirá una ventana con el resultado. Presiona el botón de guardado para exportar tu documento unificado en formato JPG, PNG o TIFF.

## 🤝 Apoya el Proyecto

Che PDF es y siempre será una herramienta de software libre y gratuita. Tu aporte voluntario nos ayuda a mantener nuestra infraestructura, desarrollar nuevas herramientas y continuar con el trabajo de investigación.

Si la herramienta te resulta útil, considera hacer un aporte solidario:
💖 Donar a través de Ko-fi: https://ko-fi.com/sitiosdememoriauy

## 👨‍💻 Autores

* Rodrigo Barbano y Mariana Risso - Investigadores y desarrolladores.
Proyecto impulsado por sitiosdememoria.uy.

## 📄 Licencia

Este proyecto está bajo la Licencia GNU GPLv3. Eres libre de usar, estudiar, compartir y modificar este software para cualquier propósito, siempre y cuando las obras derivadas mantengan la misma licencia abierta.

## Historial de Versiones
### v0.4 (Abril 2026)
* Versión inicial estable del proyecto.
