from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional
from pydantic import BaseModel
from app.services.db_service import db_service
from app.exceptions import DatabaseError, TableNotFoundError, QueryError, ValidationError

router = APIRouter(prefix="/api/db", tags=["database"])

class QueryRequest(BaseModel):
    query: str

@router.get("/tables")
async def list_tables():
    """Lista todas las tablas disponibles en la base de datos"""
    try:
        return await db_service.list_tables()
    except DatabaseError as e:
        raise HTTPException(status_code=e.code, detail=e.message)

@router.get("/tables/{table_name}")
async def get_table_content(
    table_name: str,
    limit: Optional[int] = Query(None, ge=1, description="Número máximo de registros a retornar"),
    offset: Optional[int] = Query(None, ge=0, description="Número de registros a saltar"),
    order_by: Optional[str] = Query(None, description="Columna por la cual ordenar"),
    order_direction: Optional[str] = Query(None, description="Dirección del ordenamiento (ASC o DESC)")
):
    """Obtiene el contenido de una tabla específica"""
    try:
        return await db_service.get_table_content(
            table_name=table_name,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction
        )
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=e.code, detail=e.message)

@router.get("/tables/{table_name}/structure")
async def get_table_structure(table_name: str):
    """Obtiene la estructura de una tabla específica"""
    try:
        return await db_service.get_table_structure(table_name)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=e.code, detail=e.message)

@router.post("/query")
async def execute_query(request: QueryRequest):
    """Ejecuta una consulta SQL personalizada"""
    try:
        return await db_service.execute_query(request.query)
    except QueryError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=e.code, detail=e.message) 