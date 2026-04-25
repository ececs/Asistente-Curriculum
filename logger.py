import json
from datetime import datetime
import os

LOG_FILE = "logs_interacciones.jsonl"

def log_interaccion(pregunta, respuesta, evaluacion_final, intentos):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "pregunta": pregunta,
        "respuesta": respuesta,
        "evaluacion_final": {
            "aceptada": evaluacion_final.es_aceptable,
            "retroalimentacion": evaluacion_final.retroalimentacion
        },
        "intentos": intentos
    }
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def obtener_estadisticas():
    if not os.path.exists(LOG_FILE):
        return "No hay logs disponibles."
    
    total = 0
    aceptadas = 0
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            total += 1
            data = json.loads(line)
            if data["evaluacion_final"]["aceptada"]:
                aceptadas += 1
    
    return f"Total: {total} | Aceptadas: {aceptadas} ({ (aceptadas/total)*100 if total > 0 else 0 }%)"
