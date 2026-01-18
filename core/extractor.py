import os
import fitz  # PyMuPDF
import pdfplumber
import pandas as pd
from pdf2docx import Converter
from docx import Document
import re
import pytesseract
from PIL import Image
import io

# --- IMPORTACIONES GMFT ---
from gmft.pdf_bindings import PyPDFium2Document
from gmft.auto import AutoTableFormatter

class PDFExtractor:
    def __init__(self, file_path, output_folder="output"):
        self.file_path = file_path
        self.filename = os.path.splitext(os.path.basename(file_path))[0]
        self.output_dir = os.path.join(output_folder, self.filename)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # --- CONFIGURACIÓN TESSERACT ---
        self.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        
        if os.path.exists(self.tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            self.has_ocr = True
            print("👁️ Motor de Visión Tesseract listo.")
        else:
            self.has_ocr = False
            print(f"⚠️ Tesseract no encontrado.")

        # Configuración GMFT
        try:
            self.formatter = AutoTableFormatter()
            self.usar_ia = True
        except:
            self.usar_ia = False

    def _clean_text(self, text):
        if text:
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text) 
            text = text.strip()
            return text if text else None
        return None

    def _has_text_content(self):
        """Verifica si el PDF tiene texto seleccionable (Digital)"""
        try:
            with fitz.open(self.file_path) as doc:
                # Revisamos hasta 3 páginas
                for i in range(min(len(doc), 3)):
                    text = doc[i].get_text()
                    # Si encontramos más de 50 caracteres, asumimos que es nativo
                    if len(text.strip()) > 50:
                        return True
            return False
        except:
            return False

    def extract_tables(self):
        """ (Este método ya funciona bien, lo dejamos igual) """
        excel_path = os.path.join(self.output_dir, f"{self.filename}_tablas.xlsx")
        tables_found = []

        # 1. IA (GMFT)
        if self.usar_ia:
            print("📊 Estrategia 1: Probando IA (GMFT)...")
            try:
                doc = PyPDFium2Document(self.file_path)
                for table in doc.tables():
                    try:
                        df = self.formatter.extract(table)
                        if not df.empty and len(df) > 1:
                            df = df.map(lambda x: self._clean_text(str(x)) if x is not None else x)
                            tables_found.append((f"P{table.page.page_number+1}_IA", df))
                    except: pass
                doc.close()
            except Exception as e: print(f"   ⚠️ Falló GMFT: {e}")

        # 2. OCR (Tesseract)
        if not tables_found and self.has_ocr:
            print("👁️ Estrategia 2: Activando Visión Artificial (OCR)...")
            ocr_tables = self._extract_with_vision_fallback()
            tables_found.extend(ocr_tables)

        # 3. Nativa
        if not tables_found:
            print("📄 Estrategia 3: Activando método nativo...")
            native_tables = self._extract_native_fallback()
            tables_found.extend(native_tables)

        if tables_found:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                for sheet_name, df in tables_found:
                    counter = 1
                    base = sheet_name
                    while sheet_name in writer.book.sheetnames:
                        sheet_name = f"{base}_{counter}"
                        counter += 1
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            print(f"✅ Excel generado con {len(tables_found)} tablas.")
            return excel_path
        return None

    def extract_text_doc_smart(self):
        """
        Genera Word. 
        - Si es digital -> Usa pdf2docx (Mantiene formato).
        - Si es imagen -> Usa OCR (Extrae texto plano editable).
        """
        print("📝 Generando documento Word...")
        docx_path = os.path.join(self.output_dir, f"{self.filename}_edit.docx")
        
        # Paso 1: Detectar si es nativo o imagen
        es_nativo = self._has_text_content()

        if es_nativo:
            print("   -> PDF Digital detectado. Usando conversión de alta fidelidad.")
            try:
                cv = Converter(self.file_path)
                cv.convert(docx_path, start=0, end=None)
                cv.close()
                return docx_path
            except Exception as e:
                print(f"   ⚠️ Falló pdf2docx: {e}. Intentando OCR...")
        
        # Paso 2: Si no es nativo (o falló el anterior), usar OCR Fuerza Bruta
        if self.has_ocr:
            print("   -> PDF Escaneado detectado. Usando OCR para texto editable...")
            doc = Document()
            doc.add_heading(f'Texto Extraído (OCR) - {self.filename}', 0)

            with fitz.open(self.file_path) as pdf:
                for i, page in enumerate(pdf):
                    print(f"      Procesando pág {i+1}...")
                    # Convertir página a imagen
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Extraer texto con Tesseract
                    texto = pytesseract.image_to_string(image, lang='spa')
                    
                    # Escribir en Word
                    doc.add_heading(f'Página {i+1}', level=1)
                    doc.add_paragraph(texto)
                    # Añadir salto de página
                    if i < len(pdf) - 1:
                        doc.add_page_break()
            
            doc.save(docx_path)
            return docx_path
        
        return None

    def _extract_with_vision_fallback(self):
        """(Tu método de OCR para tablas, se mantiene igual)"""
        found_tables = []
        try:
            with fitz.open(self.file_path) as doc:
                for i in range(len(doc)):
                    page = doc[i]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))

                    # data frame OCR
                    data = pytesseract.image_to_data(image, lang='spa', output_type=pytesseract.Output.DATAFRAME)
                    data = data[data.conf > 30] 
                    data = data[data.text.notna()]
                    data['text'] = data['text'].astype(str).str.strip()
                    data = data[data['text'] != '']

                    if not data.empty:
                        data['row_group'] = (data['top'] // 15)
                        rows = []
                        for _, line in data.groupby('row_group'):
                            sorted_line = line.sort_values('left')
                            rows.append(sorted_line['text'].tolist())

                        if len(rows) > 1:
                            max_cols = max(len(r) for r in rows)
                            normalized_rows = [r + [''] * (max_cols - len(r)) for r in rows]
                            df = pd.DataFrame(normalized_rows)
                            found_tables.append((f"P{i+1}_OCR", df))
                            print(f"      ✨ Tabla OCR detectada en Pág {i+1}")
        except: pass
        return found_tables

    def _extract_native_fallback(self):
        """(Tu método nativo, se mantiene igual)"""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             #By Vctor Noguera at VHNGROUP
        tables = []
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    extracted = page.extract_tables()
                    for t in extracted:
                        if t:
                            df = pd.DataFrame(t[1:], columns=t[0])
                            tables.append((f"P{i+1}_Nativa", df))
        except: pass
        return tables

    def extract_images(self):
        """(Tu método de imágenes, se mantiene igual)"""
        print("🖼️ Extrayendo imágenes...")
        img_count = 0
        images_dir = os.path.join(self.output_dir, "imagenes")
        os.makedirs(images_dir, exist_ok=True)
        with fitz.open(self.file_path) as doc:
            for i in range(len(doc)):
                for img_idx, img in enumerate(doc[i].get_images(full=True)):
                    try:
                        base = doc.extract_image(img[0])
                        with open(os.path.join(images_dir, f"P{i+1}_{img_idx}.{base['ext']}"), "wb") as f:
                            f.write(base["image"])
                        img_count += 1
                    except: pass
        return img_count