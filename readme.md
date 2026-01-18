# Data Extractor (Híbrido: AI + OCR + Nativo)

Una aplicación web robusta construida con **Flask** para extraer datos estructurados de documentos PDF. Utiliza una arquitectura inteligente "en cascada" para manejar desde documentos digitales perfectos hasta escaneos complejos e imágenes.

---

## Características Principales

* **Extracción de Tablas Híbrida:**
    1.  **Nivel 1 (IA):** Usa **GMFT (Graph Matching for Tables)** para detectar tablas complejas o rotadas mediante Deep Learning.
    2.  **Nivel 2 (Visión/OCR):** Usa **Tesseract 5.5** para "leer" píxeles en imágenes o escaneos planos.
    3.  **Nivel 3 (Nativo):** Usa **pdfplumber** para documentos digitales estándar (rápido).
* **Conversión a Word Inteligente:**
    * Mantiene el formato si el PDF es digital (`pdf2docx`).
    * Extrae texto editable mediante OCR si el PDF es una imagen.
* **Extracción de Activos:** Separa todas las imágenes embebidas en alta calidad.
* **Interfaz Moderna:** Frontend reactivo con Tailwind CSS y feedback de progreso en tiempo real.

---

## Requisitos Previos

Antes de instalar las dependencias de Python, asegúrate de tener instalado en tu sistema Windows:

1.  **Python 3.10 o superior** (Probado en 3.12).
2.  **Tesseract OCR (Obligatorio para escaneos):**
    * Descargar: [Tesseract-OCR-w64-setup.exe](https://github.com/UB-Mannheim/tesseract/wiki)
    * **Importante:** Durante la instalación, marca **"Spanish"** en *Additional Script Data*.
    * Ruta de instalación requerida: `C:\Program Files\Tesseract-OCR\tesseract.exe`
    * *(Si cambias esta ruta, debes actualizarla en `core/extractor.py`)*.

---

## Instalación

1.  **Crear entorno virtual:**
    ```powershell
    python -m venv .venv
    ```

2.  **Activar entorno:**
    ```powershell
    .\.venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    *(Nota: Esto descargará aprox. 2GB debido a las librerías de IA como Torch y Transformers)*.
    ```powershell
    pip install -r requirements.txt
    ```

---

## Ejecución

1.  Asegúrate de tener el entorno virtual activado.
2.  Ejecuta el servidor:
    ```powershell
    python app.py
    ```
3.  Abre tu navegador y ve a:
    **http://127.0.0.1:5000**

---

## Estructura del Proyecto

```text
PDF_Extractor_Pro/
├── core/
│   ├── extractor.py    # CEREBRO: Lógica híbrida (GMFT, Tesseract, Plumber)
│   └── __init__.py
├── input/              # Almacenamiento temporal de subidas
├── output/             # Resultados generados antes de comprimir
├── templates/
│   └── index.html      # Frontend con Tailwind CSS + JS Fetch
├── app.py              # Servidor Flask y controlador
├── requirements.txt    # Lista de librerías
└── README.md           # Documentación


## Proyecto creado por: 

**Victor Noguera**
**issvictornoguera@gmail.com**
**licencia: MIT**

---

## Agradecimientos

* **GMFT:** [GMFT GitHub](https://github.com/UB-Mannheim/gmft)
* **Tesseract:** [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract)
* **Flask:** [Flask GitHub](https://github.com/pallets/flask)
* **PyMuPDF:** [PyMuPDF GitHub](https://github.com/pymupdf/PyMuPDF)
* **pdfplumber:** [pdfplumber GitHub](https://github.com/jsvine/pdfplumber)
* **pdf2docx:** [pdf2docx GitHub](https://github.com/AlfredoRamos/pdf2docx)
* **python-docx:** [python-docx GitHub](https://github.com/mirumee/python-docx)
* **OpenCV:** [OpenCV GitHub](https://github.com/opencv/opencv)
* **Pillow:** [Pillow GitHub](https://github.com/python-pillow/Pillow)
* **PyTorch:** [PyTorch GitHub](https://github.com/pytorch/pytorch)
* **Transformers:** [Transformers GitHub](https://github.com/huggingface/transformers)
* **Timm:** [Timm GitHub](https://github.com/rwightman/pytorch-image-models)
