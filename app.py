# By Victor Noguera de VHNGROUP
import os
import shutil
import time
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from core.extractor import PDFExtractor

app = Flask(__name__)
app.secret_key = "Esta_Es_Una_Clave_Ultra_Secreta_NO_using_In_Producction"

# Configuración de carpetas (input/output)                                                                                                                                                                                                                                                                                                                                                                                                                                              By Victor Noguera de VHNGROUP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'input')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')

# Asegurar que existan
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# --- CONFIGURACIÓN DE RETENCIÓN ---
HOURS_TO_KEEP = 12  # Tiempo en horas antes de borrar un archivo procesado

def limpiar_archivos_antiguos():
    """
    Borra archivos/carpetas en 'output' que sean más antiguos de 12 horas.
    Usa la fecha de modificación del sistema de archivos.
    """
    folder = app.config['OUTPUT_FOLDER']
    
    # Calcular el tiempo límite (Ahora - 12 horas en segundos)
    current_time = time.time()
    limit_time = current_time - (HOURS_TO_KEEP * 3600)
    
    print(f" Verificando archivos antiguos (>{HOURS_TO_KEEP}h) en output...")
    
    deleted_count = 0
    
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        
        try:
            # Obtener la fecha de modificación del archivo/carpeta
            file_mod_time = os.path.getmtime(file_path)
            
            # Si el archivo es más viejo que el límite...
            if file_mod_time < limit_time:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path) # Borrar archivo/zip
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path) # Borrar carpeta de extracción
                
                print(f"   🗑️ Eliminado por antigüedad: {filename}")
                deleted_count += 1
                
        except Exception as e:
            print(f"   ⚠️ Error intentando borrar {filename}: {e}")
    
    if deleted_count == 0:
        print("   ✅ No hubo archivos caducados para borrar.")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400

    if file:
        # --- PASO 0: MANTENIMIENTO ---
        # Ejecutamos la limpieza inteligente antes de procesar
        limpiar_archivos_antiguos()

        start_time = time.time()
        
        # 1. Guardar archivo
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        filename_unique = f"{timestamp}_{filename}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_unique)
        file.save(file_path)
        
        print(f"\n INICIANDO PROCESO PARA: {filename}")

        try:
            # 2. Instanciar el Extractor
            extractor = PDFExtractor(file_path, output_folder=OUTPUT_FOLDER)
            
            # 3. Ejecutar los módulos
            print("   -> Paso 1/3: Imágenes...")
            extractor.extract_images()
            
            print("   -> Paso 2/3: Tablas (IA/Nativo)...")
            extractor.extract_tables()

            print("   -> Paso 3/3: Documento Word...")
            extractor.extract_text_doc_smart()

            # 4. Comprimir resultados
            print(" Comprimiendo archivos...")
            folder_to_zip = extractor.output_dir
            zip_filename = f"Procesado_{os.path.splitext(filename)[0]}"
            zip_path_base = os.path.join(OUTPUT_FOLDER, zip_filename)
            
            zip_full_path = shutil.make_archive(zip_path_base, 'zip', folder_to_zip)
            
            elapsed = time.time() - start_time
            print(f"✅ PROCESO COMPLETADO en {elapsed:.2f} segundos.\n")

            return send_file(zip_full_path, as_attachment=True)

        except Exception as e:
            print(f" ERROR CRÍTICO: {str(e)}")
            return f"Ocurrió un error en el servidor: {str(e)}", 500
        
        finally:
            # Limpieza del INPUT (El PDF temporal siempre se borra al instante)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except: pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)