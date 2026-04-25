from pypdf import PdfReader
import os

def extraer_datos():
    # 1. Extracción de PDF
    lector = PdfReader("curriculum.pdf")
    perfil = ""
    for page in lector.pages:
        texto = page.extract_text()
        if texto:
            perfil += texto

    # 2. Extracción de Resumen
    resumen = ""
    archivo_resumen = "resumen.txt"
    if os.path.exists(archivo_resumen):
        with open(archivo_resumen, "r", encoding="utf-8") as f:
            resumen = f.read()
    
    return perfil, resumen
