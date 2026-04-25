import gradio as gr
from config import client_openai, MODEL_CHAT
from extractor import extraer_datos
from engine import generar_prompts, evaluar_respuesta, corregir_respuesta

# 1. Cargar datos y prompts
perfil, resumen = extraer_datos()
prompt_sistema, prompt_evaluador = generar_prompts(perfil, resumen)

def chatear(mensaje, historial):
    print(f"\n--- Pregunta: {mensaje[:50]}... ---", flush=True)
    
    # Generar respuesta
    mensajes = [{"role": "system", "content": prompt_sistema}] + historial + [{"role": "user", "content": mensaje}]
    respuesta = client_openai.chat.completions.create(model=MODEL_CHAT, messages=mensajes)
    respuesta_chat = respuesta.choices[0].message.content

    # Evaluar
    evaluacion = evaluar_respuesta(respuesta_chat, mensaje, historial, prompt_evaluador)

    if evaluacion.es_aceptable:
        print(">>> [OK] Respuesta aceptada.", flush=True)
        return respuesta_chat
    else:
        print(f">>> [RECHAZO] Motivo: {evaluacion.retroalimentacion}", flush=True)
        return corregir_respuesta(respuesta_chat, mensaje, historial, evaluacion.retroalimentacion, prompt_sistema)

# 2. Interfaz
print("Iniciando Asistente Modular...", flush=True)
demo = gr.ChatInterface(chatear)
demo.launch(prevent_thread_lock=True)

print("\n>>> Escribe 'salir' para cerrar el programa.\n", flush=True)

while True:
    if input().strip().lower() == "salir":
        print("Cerrando...", flush=True)
        demo.close()
        break