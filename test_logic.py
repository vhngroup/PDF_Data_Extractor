from core.extractor import PDFExtractor
import os

# Define la ruta de tu PDF de prueba
pdf_path = os.path.join("input", "prueba.pdf") # Asegúrate que este archivo exista

# Verifica si pusiste el archivo
if not os.path.exists(pdf_path):
    print(f"❌ ERROR: No encontré el archivo en {pdf_path}")
    print("Por favor coloca un PDF en la carpeta 'input' y llámalo 'prueba.pdf'")
else:
    try:
        # 1. Instanciamos el procesador
        extractor = PDFExtractor(pdf_path)
        
        # 2. Ejecutamos extracciones
        path_excel = extractor.extract_tables()
        print(f"✅ Excel guardado en: {path_excel}")
        
        num_imgs = extractor.extract_images()
        print(f"✅ Se extrajeron {num_imgs} imágenes.")
        
        path_doc = extractor.extract_text_doc_smart()
        print(f"✅ Word guardado en: {path_doc}")
        
        print("\n✨ Proceso finalizado con éxito.")
        
    except Exception as e:
        print(f"💥 Ocurrió un error fatal: {e}")