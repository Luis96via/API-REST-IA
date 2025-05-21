import os
from openai import AsyncOpenAI
from typing import List, Dict, Any
from app.models import ChatMessage, ChatResponse

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.default_model = os.getenv("MODEL_NAME", "deepseek/deepseek-r1:free")

    async def process_chat(self, messages: List[ChatMessage], model: str = None, temperature: float = 0.7, max_tokens: int = None) -> ChatResponse:
        try:
            # Preparar los parámetros de la llamada
            params = {
                "model": model or self.default_model,
                "messages": [msg.dict() for msg in messages],
                "temperature": temperature
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens

            # Realizar la llamada a la API
            response = await self.client.chat.completions.create(**params)
            
            # Procesar la respuesta
            return ChatResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            raise Exception(f"Error al procesar la solicitud de chat: {str(e)}")

# Instancia global del servicio
ai_service = AIService() 