import pandas as pd
import pdfplumber
import fitz # Esto es PyMuPDF
import flask
from docx import Document

print("✅ Entorno configurado correctamente.")
print(f"   - Pandas versión: {pd.__version__}")
print(f"   - PDFPlumber versión: {pdfplumber.__version__}")
print(f"   - PyMuPDF (Fitz) versión: {fitz.__version__}")
print(f"   - Flask versión: {flask.__version__}")