import os
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from app.models import ChatMessage, ChatResponse
from app.services.mcp_service import mcp_service
import json
import httpx
from app.exceptions import DatabaseError, TableNotFoundError, QueryError, ValidationError
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno explícitamente
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"\n[AI Service] Buscando .env en: {BASE_DIR}")
load_dotenv(BASE_DIR / ".env")

class AIService:
    def __init__(self):
        print("\n[AI Service] Inicializando servicio AI...")
        print(f"[AI Service] OPENAI_API_KEY existe: {bool(os.getenv('OPENAI_API_KEY'))}")
        print(f"[AI Service] OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
        self.model_name = os.getenv('MODEL_NAME', 'gpt-3.5-turbo-1106')
        print(f"[AI Service] MODEL_NAME: {self.model_name}")
        
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "HTTP-Referer": os.getenv("SITE_URL", "http://localhost:3000"),
                "X-Title": os.getenv("SITE_NAME", "API REST Python MCP"),
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
        )
        
        # Verificar que tenemos la clave de API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[AI Service] ❌ No se encontró OPENAI_API_KEY")
            print(f"[AI Service] Variables de entorno disponibles: {list(os.environ.keys())}")
            raise ValueError("No se encontró la clave de API de OpenRouter (OPENAI_API_KEY)")
        print("[AI Service] ✅ OPENAI_API_KEY encontrada")
        
        # Definir las herramientas disponibles
        self.tools = [{
            "type": "function",
            "function": {
                "name": "execute_mcp_command",
                "description": """
                Ejecuta comandos MCP para interactuar con la base de datos PostgreSQL.
                
                Acciones disponibles:
                1. list_tables: Lista todas las tablas disponibles
                2. describe_table: Obtiene la estructura de una tabla específica
                3. execute_query: Ejecuta una consulta SQL personalizada
                4. get_table_content: Obtiene el contenido de una tabla específica
                
                Ejemplos:
                - Para listar tablas: {"action": "list_tables"}
                - Para describir una tabla: {"action": "describe_table", "table_name": "categories"}
                - Para ejecutar una consulta: {"action": "execute_query", "query": "SELECT * FROM categories"}
                - Para obtener contenido: {"action": "get_table_content", "table_name": "categories"}
                """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list_tables", "describe_table", "execute_query", "get_table_content"],
                            "description": "La acción a ejecutar"
                        },
                        "table_name": {
                            "type": "string",
                            "description": "Nombre de la tabla (requerido para describe_table y get_table_content)"
                        },
                        "query": {
                            "type": "string",
                            "description": "Consulta SQL a ejecutar (requerido para execute_query)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Número máximo de registros a retornar (opcional para get_table_content)"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Número de registros a saltar (opcional para get_table_content)"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Columna por la cual ordenar (opcional para get_table_content)"
                        },
                        "order_direction": {
                            "type": "string",
                            "enum": ["ASC", "DESC"],
                            "description": "Dirección del ordenamiento (opcional para get_table_content)"
                        }
                    },
                    "required": ["action"]
                }
            }
        }]
        
        # Mensaje del sistema para guiar al modelo
        self.system_message = """Eres un asistente especializado en bases de datos PostgreSQL.
Tu tarea es ayudar a los usuarios a interactuar con la base de datos de manera segura y eficiente.

Instrucciones específicas:
1. Para consultas simples sobre tablas, usa la acción get_table_content
2. Para ver la estructura de una tabla, usa describe_table
3. Para listar todas las tablas, usa list_tables
4. Para consultas personalizadas, usa execute_query

Ejemplos de cómo procesar consultas:
- "¿Qué tablas hay disponibles?" -> Usar list_tables
- "¿Qué contiene la tabla categories?" -> Usar get_table_content con table_name="categories"
- "¿Cómo está estructurada la tabla products?" -> Usar describe_table con table_name="products"
- "¿Cuántos productos hay por categoría?" -> Usar execute_query con una consulta SQL apropiada

IMPORTANTE:
- Siempre usa la acción más específica posible
- Valida que los parámetros requeridos estén presentes
- Maneja los errores de manera amigable
- Proporciona respuestas claras y concisas
"""

    async def process_chat(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None
    ) -> dict:
        """Procesa un mensaje del usuario y genera una respuesta"""
        try:
            # Preparar los mensajes para la API
            api_messages = [
                {"role": "system", "content": self.system_message},
                *[{"role": msg.role, "content": msg.content} for msg in messages]
            ]
            
            # Llamar a la API de OpenAI
            response = await self.client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": model or self.model_name,
                    "messages": api_messages,
                    "tools": self.tools,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Error en la API: {response.text}")
                
            data = response.json()
            message = data["choices"][0]["message"]
            
            # Si hay llamadas a herramientas, procesarlas
            if "tool_calls" in message:
                tool_calls = message["tool_calls"]
                results = []
                
                for tool_call in tool_calls:
                    try:
                        # Extraer los argumentos de la llamada
                        args = tool_call["function"]["arguments"]
                        if isinstance(args, str):
                            args = json.loads(args)
                            
                        # Ejecutar el comando MCP
                        result = await mcp_service.execute_mcp_command(
                            action=args["action"],
                            **{k: v for k, v in args.items() if k != "action"}
                        )
                        
                        results.append({
                            "tool_call_id": tool_call["id"],
                            "result": result
                        })
                        
                    except (DatabaseError, TableNotFoundError, QueryError, ValidationError) as e:
                        results.append({
                            "tool_call_id": tool_call["id"],
                            "error": str(e)
                        })
                    except Exception as e:
                        results.append({
                            "tool_call_id": tool_call["id"],
                            "error": f"Error inesperado: {str(e)}"
                        })
                
                # Preparar los mensajes para la segunda llamada
                messages = [
                    {"role": "system", "content": self.system_message},
                    *[{"role": msg.role, "content": msg.content} for msg in messages],
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": tool_calls
                    }
                ]
                
                # Añadir los resultados de las herramientas
                for result in results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": result["tool_call_id"],
                        "content": json.dumps(result["result"] if "result" in result else {"error": result["error"]})
                    })
                
                # Enviar los resultados al modelo
                response = await self.client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json={
                        "model": model or self.model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Error en la API: {response.text}")
                    
                data = response.json()
                processed_response = await self._process_openrouter_response(data)
                processed_response["tool_results"] = results
                return processed_response
            
            # Procesar la respuesta normal
            return await self._process_openrouter_response(data)
            
        except Exception as e:
            print(f"Error al procesar el chat: {str(e)}")
            raise
            
    async def close(self):
        """Cierra el cliente HTTP"""
        await self.client.aclose()

    async def _process_openrouter_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la respuesta de OpenRouter y la adapta a nuestro formato."""
        try:
            # Extraer la respuesta del modelo
            model_response = response.get("choices", [{}])[0].get("message", {})
            content = model_response.get("content", "")
            
            # Procesar el uso de tokens
            usage_data = response.get("usage", {})
            prompt_details = usage_data.get("prompt_tokens_details", {})
            completion_details = usage_data.get("completion_tokens_details", {})
            
            # Construir la respuesta en nuestro formato
            return {
                "content": content,
                "model": response.get("model", self.model_name),
                "usage": {
                    "prompt_tokens": usage_data.get("prompt_tokens", 0),
                    "completion_tokens": usage_data.get("completion_tokens", 0),
                    "total_tokens": usage_data.get("total_tokens", 0),
                    "prompt_tokens_details": {
                        "cached_tokens": prompt_details.get("cached_tokens", 0),
                        "reasoning_tokens": prompt_details.get("reasoning_tokens", 0),
                        "total_tokens": prompt_details.get("total_tokens", 0)
                    } if prompt_details else None,
                    "completion_tokens_details": {
                        "cached_tokens": completion_details.get("cached_tokens", 0),
                        "reasoning_tokens": completion_details.get("reasoning_tokens", 0),
                        "total_tokens": completion_details.get("total_tokens", 0)
                    } if completion_details else None
                },
                "tool_results": None  # Por ahora no manejamos resultados de herramientas
            }
        except Exception as e:
            print(f"Error procesando respuesta de OpenRouter: {str(e)}")
            print(f"Respuesta original: {json.dumps(response, indent=2)}")
            raise

# Instancia global del servicio AI
ai_service = AIService() 