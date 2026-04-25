from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from pydantic import BaseModel

load_dotenv(override=True)
client_openai = OpenAI()

# Configuración de Gemini como evaluador (vía API compatible con OpenAI)
gemini = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Definición del esquema de respuesta para el evaluador
class Evaluacion(BaseModel):
    es_aceptable: bool
    retroalimentacion: str

# 1. Extracción de información del Curriculum
lector = PdfReader("curriculum.pdf")
perfil = ""
for page in lector.pages:
    texto = page.extract_text()
    if texto:
        perfil += texto

with open("resumen.txt", "r", encoding="utf-8") as f:
    resumen = f.read()

nombre = "Eudaldo Alvaro Cal Saul"

# 2. Configuración del sistema de Chat Principal
prompt_sistema = f"""Estas actuando como {nombre}. Estas respondiendo preguntas en el sitio web de {nombre}, 
particularmente preguntas relacionadas con la carrera, antecedentes, habilidades y experiencia de {nombre}. 
Tu responsabilidad es representar a {nombre} de la manera más fiel posible. 
Se profesional y atractivo, como si hablaras con un cliente potencial o futuro empleador.
Si no sabes la respuesta, dilo.

## Resumen:
{resumen}

## Perfil de LinkedIn:
{perfil}

Con este contexto, por favor chatea con el usuario, manteniéndote siempre en el personaje de {nombre}.
"""

# 3. Configuración del Sistema Evaluador
prompt_sistema_evaluador = f"""Eres un evaluador de calidad. Tu tarea es decidir si la respuesta del Agente es aceptable.
El Agente interpreta a {nombre} en su sitio web personal.
La respuesta debe ser profesional, fiel a los antecedentes de {nombre} y atractiva.

## Información de contexto de {nombre}:
{resumen}
{perfil}

Evalúa si la respuesta es veraz según el contexto y si mantiene el tono adecuado.
"""

def generar_prompt_usuario_evaluador(respuesta_agente, mensaje_usuario, historial):
    prompt = f"Historial de conversación:\n{historial}\n\n"
    prompt += f"Último mensaje del usuario: {mensaje_usuario}\n"
    prompt += f"Respuesta a evaluar: {respuesta_agente}\n\n"
    prompt += "Responde en formato JSON si la respuesta es aceptable y proporciona retroalimentación."
    return prompt

def evaluar_respuesta(respuesta_chat, mensaje, historial) -> Evaluacion:
    try:
        mensajes = [
            {"role": "system", "content": prompt_sistema_evaluador},
            {"role": "user", "content": generar_prompt_usuario_evaluador(respuesta_chat, mensaje, historial)}
        ]
        completion = gemini.chat.completions.create(
            model="gemini-1.5-flash", 
            messages=mensajes, 
            response_format=Evaluacion
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"Error en evaluación: {e}")
        # En caso de error en el evaluador, dejamos pasar la respuesta original por seguridad
        return Evaluacion(es_aceptable=True, retroalimentacion="")

def reejecutar_con_correccion(respuesta_fallida, mensaje, historial, retroalimentacion):
    prompt_corregido = prompt_sistema + f"\n\n## ATENCIÓN: Tu respuesta anterior fue rechazada por control de calidad.\n"
    prompt_corregido += f"Tu intento anterior: {respuesta_fallida}\n"
    prompt_corregido += f"Razón del rechazo: {retroalimentacion}\n"
    prompt_corregido += "Por favor, genera una nueva respuesta corregida siguiendo las instrucciones."
    
    mensajes = [{"role": "system", "content": prompt_corregido}] + historial + [{"role": "user", "content": mensaje}]
    nueva_respuesta = client_openai.chat.completions.create(model="gpt-4o-mini", messages=mensajes)
    return nueva_respuesta.choices[0].message.content

def chatear(mensaje, historial):
    # Generar respuesta inicial
    mensajes = [{"role": "system", "content": prompt_sistema}] + historial + [{"role": "user", "content": mensaje}]
    respuesta = client_openai.chat.completions.create(model="gpt-4o-mini", messages=mensajes)
    respuesta_chat = respuesta.choices[0].message.content

    # Evaluar respuesta
    evaluacion = evaluar_respuesta(respuesta_chat, mensaje, historial)

    if evaluacion.es_aceptable:
        print(">>> Respuesta aceptada.")
        return respuesta_chat
    else:
        print(f">>> Respuesta rechazada. Motivo: {evaluacion.retroalimentacion}")
        # Reintentar una vez con la corrección
        respuesta_corregida = reejecutar_con_correccion(respuesta_chat, mensaje, historial, evaluacion.retroalimentacion)
        return respuesta_corregida

# 4. Lanzamiento de la Interfaz
print("Iniciando Interfaz de Chat...")
gr.ChatInterface(chatear).launch()