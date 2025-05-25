from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Procesa un mensaje del usuario y genera una respuesta usando el servicio AI"""
    try:
        result = await ai_service.process_chat(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 