from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str = Field(..., description="El rol del mensaje (system, user, assistant)")
    content: str = Field(..., description="El contenido del mensaje")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Lista de mensajes para la conversación")
    model: Optional[str] = Field(None, description="Modelo a utilizar (opcional, por defecto se usa el configurado)")
    temperature: Optional[float] = Field(0.7, description="Temperatura para la generación (0.0 a 1.0)")
    max_tokens: Optional[int] = Field(None, description="Número máximo de tokens a generar")

class ChatResponse(BaseModel):
    content: str = Field(..., description="La respuesta generada por el modelo")
    model: str = Field(..., description="El modelo utilizado para generar la respuesta")
    usage: Dict[str, int] = Field(..., description="Información sobre el uso de tokens") 