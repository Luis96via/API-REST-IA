from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.models import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Chat con OpenRouter",
    description="API REST base desarrollada por Luis AVR como fundamento para un sistema más ambicioso. Esta implementación inicial establece la base para la integración de Function Calling y la implementación del protocolo MCP (Model-Controller-Protocol) con agentes inteligentes. Diseñada con una arquitectura modular y extensible, esta API representa el primer paso hacia un sistema más complejo que permitirá la interacción avanzada con modelos de lenguaje y la ejecución de tareas específicas a través de agentes especializados.",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint para procesar mensajes de chat y obtener respuestas del modelo.
    """
    try:
        response = await ai_service.process_chat(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API.
    """
    return {
        "status": "ok",
        "message": "API funcionando correctamente",
        "model": os.getenv("MODEL_NAME", "deepseek/deepseek-r1:free")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 