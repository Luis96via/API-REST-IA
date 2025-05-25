import contextlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path
from app.routers import chat_router, db_router, pedido_router
from app.config import settings

# Obtener la ruta absoluta al directorio del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde el archivo .env
load_dotenv(BASE_DIR / ".env")

# Verificar que las variables de entorno necesarias están cargadas
required_env_vars = ["DATABASE_URL", "OPENAI_API_KEY", "OPENAI_BASE_URL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

from app.models import ChatRequest, ChatResponse
from app.services.ai_service import ai_service
from app.services.mcp_service import mcp_service

# Crear la aplicación FastAPI con manejo del ciclo de vida
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación, incluyendo el servidor MCP
    """
    # El servidor MCP se inicia automáticamente al montarlo en la aplicación
    yield
    # La limpieza se maneja automáticamente

# Crear la aplicación FastAPI
app = FastAPI(
    title="API REST Python MCP",
    description="API REST para interactuar con la base de datos PostgreSQL usando MCP",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar el servidor MCP en la ruta /mcp (o "http://localhost:8080/mcp")
print("Montando /mcp en el servidor MCP (FastAPI)…")

# Crear un endpoint específico para MCP
@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """
    Endpoint para manejar las peticiones MCP
    """
    try:
        print(f"[DEBUG] Recibida petición MCP: {request}")  # Debug
        action = request.get("action")
        params = request.get("params", {})
        
        if not action:
            raise HTTPException(status_code=400, detail="Se requiere el parámetro 'action'")
            
        result = await mcp_service.execute_mcp_command(
            server_name="postgres",  # Nombre por defecto
            action=action,
            params=params
        )
        return result
    except Exception as e:
        print(f"[ERROR] Error en endpoint MCP: {str(e)}")  # Debug
        raise HTTPException(status_code=500, detail=str(e))

print("Endpoint MCP registrado en /mcp")  # Debug

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint para procesar mensajes de chat y obtener respuestas del modelo.
    El modelo puede ejecutar comandos MCP cuando sea necesario.
    """
    try:
        # Imprimir información de depuración
        print(f"Modelo solicitado: {request.model}")
        print(f"Modelo por defecto: {os.getenv('MODEL_NAME')}")
        print(f"Base URL: {os.getenv('OPENAI_BASE_URL')}")
        
        response = await ai_service.process_chat(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return ChatResponse(**response)
    except Exception as e:
        # Imprimir el error completo para depuración
        import traceback
        error_details = traceback.format_exc()
        print(f"Error detallado: {error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar la solicitud: {str(e)}\nDetalles: {error_details}"
        )

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API y los servicios MCP.
    """
    return {
        "status": "ok",
        "message": "API funcionando correctamente",
        "model": os.getenv("MODEL_NAME", "openai/gpt-3.5-turbo-1106"),
        "mcp_server": {
            "status": "running",
            "mount_path": "/mcp",
            "transport": "streamable-http"
        },
        "env_vars_loaded": {var: bool(os.getenv(var)) for var in required_env_vars}
    }

@app.get("/test-config")
async def test_config():
    """
    Endpoint para verificar la configuración de OpenRouter.
    """
    return {
        "openrouter_config": {
            "api_key_exists": bool(os.getenv("OPENAI_API_KEY")),
            "api_key_length": len(os.getenv("OPENAI_API_KEY", "")) if os.getenv("OPENAI_API_KEY") else 0,
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "model": os.getenv("MODEL_NAME"),
            "site_url": os.getenv("SITE_URL"),
            "site_name": os.getenv("SITE_NAME")
        }
    }

@app.get("/test-mcp")
async def test_mcp():
    """
    Endpoint de prueba para verificar la configuración del servidor MCP
    """
    return {
        "mcp_status": "mounted",
        "mcp_path": "/mcp",
        "available_tools": list(mcp_service.registered_tools.keys()),
        "mcp_instance": str(mcp_service.mcp),
        "mcp_methods": [method for method in dir(mcp_service.mcp) if not method.startswith('_')]
    }

# Incluir routers
app.include_router(chat_router.router)
app.include_router(db_router.router)
app.include_router(pedido_router.router)

@app.get("/")
async def root():
    """Endpoint raíz que devuelve información básica de la API"""
    return {
        "message": "Bienvenido a la API REST Python MCP",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "database": {
                "list_tables": "/api/db/tables",
                "get_table_content": "/api/db/tables/{table_name}",
                "get_table_structure": "/api/db/tables/{table_name}/structure",
                "execute_query": "/api/db/query"
            },
            "pedidos": {
                "crear_pedido": "/api/pedidos"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 