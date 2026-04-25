import gradio as gr
from config import client_openai, MODEL_CHAT
from extractor import extraer_datos
from engine import generar_prompts, evaluar_respuesta, corregir_respuesta
from vector_store import indexar_texto, buscar_contexto
from logger import log_interaccion, obtener_estadisticas

# 1. Cargar datos e indexar en la Base de Datos Vectorial (RAG)
perfil, resumen = extraer_datos()
indexar_texto(perfil, "curriculum_pdf")
indexar_texto(resumen, "resumen_txt")

# Generar prompts base (ahora el prompt de sistema será más dinámico)
prompt_sistema_base, prompt_evaluador = generar_prompts(perfil, resumen)

def chatear(mensaje, historial):
    print(f"\n--- Pregunta: {mensaje[:50]}... ---", flush=True)
    
    # [RAG] Buscar contexto relevante para la pregunta específica
    contexto_relevante = buscar_contexto(mensaje)
    
    # Construir el prompt del sistema con el contexto recuperado
    prompt_con_contexto = prompt_sistema_base + f"\n\n## CONTEXTO RELEVANTE RECUPERADO:\n{contexto_relevante}\n"
    
    # Generar respuesta inicial
    mensajes = [{"role": "system", "content": prompt_con_contexto}] + historial + [{"role": "user", "content": mensaje}]
    respuesta = client_openai.chat.completions.create(model=MODEL_CHAT, messages=mensajes)
    respuesta_chat = respuesta.choices[0].message.content

    # Evaluar y Corregir (Bucle de Refinamiento de hasta 3 intentos)
    intentos = 0
    max_intentos = 3
    
    while intentos < max_intentos:
        evaluacion = evaluar_respuesta(respuesta_chat, mensaje, historial, prompt_evaluador)
        
        if evaluacion.es_aceptable:
            print(f">>> [OK] Respuesta aceptada en el intento {intentos + 1}.", flush=True)
            log_interaccion(mensaje, respuesta_chat, evaluacion, intentos + 1)
            return respuesta_chat
        
        intentos += 1
        print(f">>> [RECHAZO] Intento {intentos}/{max_intentos}. Motivo: {evaluacion.retroalimentacion}", flush=True)
        
        if intentos < max_intentos:
            print(">>> [REFINE] Generando respuesta corregida...", flush=True)
            respuesta_chat = corregir_respuesta(respuesta_chat, mensaje, historial, evaluacion.retroalimentacion, prompt_con_contexto)
    
    print(">>> [WARN] Se alcanzó el máximo de reintentos. Devolviendo la última versión.", flush=True)
    log_interaccion(mensaje, respuesta_chat, evaluacion, max_intentos)
    return respuesta_chat


# 2. Interfaz
print("Iniciando Asistente con RAG (Base de Datos Vectorial)...", flush=True)
demo = gr.ChatInterface(chatear)
demo.launch(prevent_thread_lock=True)

print("\n>>> Escribe 'salir' para cerrar el programa.\n", flush=True)

while True:
    if input().strip().lower() == "salir":
        print("Cerrando...", flush=True)
        demo.close()
        break