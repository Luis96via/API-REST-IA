from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="El rol del mensaje (system, user, assistant)")
    content: str = Field(..., description="El contenido del mensaje")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Lista de mensajes para la conversación")
    model: Optional[str] = Field(None, description="Modelo a utilizar (opcional, por defecto se usa el configurado)")
    temperature: Optional[float] = Field(0.7, description="Temperatura para la generación (0.0 a 1.0)")
    max_tokens: Optional[int] = Field(None, description="Número máximo de tokens a generar")

class TokenDetails(BaseModel):
    cached_tokens: Optional[int] = 0
    reasoning_tokens: Optional[int] = 0
    total_tokens: Optional[int] = 0

class UsageDetails(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    prompt_tokens_details: Optional[TokenDetails] = None
    completion_tokens_details: Optional[TokenDetails] = None

class ChatResponse(BaseModel):
    content: str = Field(..., description="La respuesta generada por el modelo")
    model: str = Field(..., description="El modelo utilizado para generar la respuesta")
    usage: Optional[UsageDetails] = Field(default_factory=UsageDetails, description="Información sobre el uso de tokens")
    tool_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Resultados de las herramientas utilizadas")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha y hora de creación de la respuesta") 