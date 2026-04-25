import chromadb
from chromadb.utils import embedding_functions
from config import client_openai, MODEL_EMBEDDING
import os

# Configuración del cliente de ChromaDB (Persistente)
db_path = os.path.join(os.getcwd(), "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)

# Usar la función de embedding de OpenAI
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=MODEL_EMBEDDING
            )

# Crear o cargar la colección
collection = chroma_client.get_or_create_collection(
    name="curriculum_chunks", 
    embedding_function=openai_ef
)

def indexar_texto(texto, source_name):
    # Fragmentar el texto en chunks de ~500 caracteres con solapamiento
    chunk_size = 500
    overlap = 100
    chunks = []
    
    for i in range(0, len(texto), chunk_size - overlap):
        chunks.append(texto[i:i + chunk_size])
    
    # Preparar datos para Chroma
    ids = [f"{source_name}_{i}" for i in range(len(chunks))]
    metadatos = [{"source": source_name} for _ in range(len(chunks))]
    
    # Añadir a la colección
    collection.upsert(
        documents=chunks,
        metadatas=metadatos,
        ids=ids
    )
    print(f">>> [RAG] {len(chunks)} fragmentos indexados desde {source_name}.", flush=True)

def buscar_contexto(pregunta, n_resultados=3):
    resultados = collection.query(
        query_texts=[pregunta],
        n_results=n_resultados
    )
    # Unir los fragmentos encontrados en un solo texto
    contexto = "\n---\n".join(resultados['documents'][0])
    return contexto
