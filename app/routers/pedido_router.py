from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.services.pedido_service import pedido_service
from app.exceptions import DatabaseError, ValidationError

router = APIRouter(prefix="/api/pedidos", tags=["pedidos"])

class ItemPedido(BaseModel):
    """Modelo para un item del pedido"""
    producto_id: int = Field(..., description="ID del producto")
    cantidad: int = Field(..., gt=0, description="Cantidad solicitada")

class CrearPedidoRequest(BaseModel):
    """Modelo para la solicitud de creación de pedido"""
    usuario_id: int = Field(..., description="ID del usuario que realiza el pedido")
    items: List[ItemPedido] = Field(..., min_items=1, description="Lista de items del pedido")

@router.post("", response_model=Dict[str, Any])
async def crear_pedido(request: CrearPedidoRequest):
    """
    Crea un nuevo pedido y actualiza el stock de los productos.
    
    Args:
        request: Datos del pedido a crear
        
    Returns:
        Dict con el resultado de la operación
    """
    try:
        # Convertir los items a diccionarios
        items = [item.dict() for item in request.items]
        
        # Crear el pedido
        return await pedido_service.crear_pedido(
            usuario_id=request.usuario_id,
            items=items
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=e.code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 