from pypdf import PdfReader
import sys

try:
    print("Abriendo curriculum.pdf...")
    lector = PdfReader("curriculum.pdf")
    print(f"Número de páginas: {len(lector.pages)}")
    perfil = ""
    for i, page in enumerate(lector.pages):
        print(f"Extrayendo página {i+1}...")
        texto = page.extract_text()
        if texto:
            perfil += texto
    print("--- Contenido extraído ---")
    print(perfil[:500] + "...") 
    print("--- Fin ---")
except Exception as e:
    print(f"Error: {e}")
