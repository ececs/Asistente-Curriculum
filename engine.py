from config import client_openai, client_gemini, MODEL_CHAT, MODEL_EVAL, NOMBRE_USUARIO
from pydantic import BaseModel

class Evaluacion(BaseModel):
    es_aceptable: bool
    retroalimentacion: str

def generar_prompts(perfil, resumen):
    prompt_sistema = f"""Estas actuando como {NOMBRE_USUARIO}. Estas respondiendo preguntas en el sitio web de {NOMBRE_USUARIO}, 
particularmente preguntas relacionadas con la carrera, antecedentes, habilidades y experiencia de {NOMBRE_USUARIO}. 
Tu responsabilidad es representar a {NOMBRE_USUARIO} de la manera más fiel posible. 
Se profesional y atractivo, como si hablaras con un cliente potencial o futuro empleador.
Si no sabes la respuesta, dilo.

## Resumen:
{resumen}

## Perfil de LinkedIn:
{perfil}

Con este contexto, por favor chatea con el usuario, manteniéndote siempre en el personaje de {NOMBRE_USUARIO}.
"""

    prompt_sistema_evaluador = f"""Eres un evaluador de calidad. Tu tarea es decidir si la respuesta del Agente es aceptable.
El Agente interpreta a {NOMBRE_USUARIO} en su sitio web personal.
La respuesta debe ser profesional, fiel a los antecedentes de {NOMBRE_USUARIO} y atractiva.

## Información de contexto de {NOMBRE_USUARIO}:
{resumen}
{perfil}

Evalúa si la respuesta es veraz según el contexto y si mantiene el tono adecuado.
"""
    return prompt_sistema, prompt_sistema_evaluador

def evaluar_respuesta(respuesta_chat, mensaje, historial, prompt_evaluador) -> Evaluacion:
    try:
        prompt_usuario = f"Historial:\n{historial}\n\nÚltimo mensaje: {mensaje}\nRespuesta a evaluar: {respuesta_chat}"
        mensajes = [
            {"role": "system", "content": prompt_evaluador},
            {"role": "user", "content": prompt_usuario}
        ]
        completion = client_gemini.chat.completions.parse(
            model=MODEL_EVAL, 
            messages=mensajes, 
            response_format=Evaluacion
        )
        print(f"Evaluando con {completion.model}...", flush=True)
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"Error en evaluación: {e}", flush=True)
        return Evaluacion(es_aceptable=True, retroalimentacion="")

def corregir_respuesta(respuesta_fallida, mensaje, historial, retroalimentacion, prompt_base):
    prompt_corregido = prompt_base + f"\n\n## CORRECCIÓN REQUERIDA:\nIntento anterior: {respuesta_fallida}\nMotivo rechazo: {retroalimentacion}"
    mensajes = [{"role": "system", "content": prompt_corregido}] + historial + [{"role": "user", "content": mensaje}]
    nueva_respuesta = client_openai.chat.completions.create(model=MODEL_CHAT, messages=mensajes)
    return nueva_respuesta.choices[0].message.content
