from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv(override=True)

# Clientes de IA
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_gemini = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Configuración de Modelos
MODEL_CHAT = "gpt-4o-mini"
MODEL_EVAL = "gemini-2.5-flash-lite"
MODEL_EMBEDDING = "text-embedding-3-small"

# Datos Personales
NOMBRE_USUARIO = "Eudaldo Alvaro Cal Saul"
