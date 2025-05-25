import os
from typing import Dict, Any, AsyncIterator, Callable, List, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path
from mcp.server.fastmcp import FastMCP, Context
import socket
import urllib.parse
import asyncio
from functools import partial
import dns.resolver
import datetime
from app.services.db_service import db_service, DatabaseService
from app.services.ai_service import AIService
from app.config import settings
from app.exceptions import DatabaseError, TableNotFoundError, QueryError, ValidationError
import logging
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

@dataclass
class AppContext:
    """Contexto de la aplicación con la conexión a la base de datos"""
    db_connection_string: str

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Maneja el ciclo de vida de la aplicación con contexto tipado"""
    # Cargar variables de entorno
    base_dir = Path(__file__).resolve().parent.parent.parent
    load_dotenv(base_dir / ".env")
    
    # Inicializar el contexto
    context = AppContext(
        db_connection_string=os.getenv("SUPABASE_DB_URL")
    )
    
    try:
        yield context
    finally:
        # La limpieza se maneja automáticamente por psycopg2
        pass

class MCPService:
    """Servicio para manejar las operaciones MCP usando el servicio de base de datos"""
    
    def __init__(self):
        """Inicializa el servicio MCP con las dependencias necesarias"""
        self.db_service = DatabaseService()
        self.ai_service = AIService()
        
    async def execute_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ejecuta un comando MCP usando el servicio de IA para interpretarlo
        
        Args:
            command: El comando MCP a ejecutar
            context: Contexto adicional para la ejecución del comando
            
        Returns:
            Dict con el resultado de la ejecución
        """
        try:
            # Validar el comando
            if not command or not isinstance(command, str):
                raise HTTPException(status_code=400, detail="El comando no puede estar vacío")
            
            # Preparar el mensaje para la IA
            system_message = """Eres un asistente especializado en interpretar comandos MCP (Modelo de Comandos de Procesamiento).
            Tu tarea es analizar el comando del usuario y determinar qué operación de base de datos realizar.
            
            Comandos disponibles:
            - LISTAR TABLAS: Muestra todas las tablas disponibles
            - MOSTRAR <tabla>: Muestra el contenido de una tabla específica
            - CONSULTAR <sql>: Ejecuta una consulta SQL personalizada
            - AYUDAR: Muestra la ayuda con los comandos disponibles
            
            Responde en formato JSON con:
            {
                "tipo": "LISTAR|MOSTRAR|CONSULTAR|AYUDAR|ERROR",
                "tabla": "nombre_tabla" (opcional),
                "sql": "consulta_sql" (opcional),
                "mensaje": "mensaje de error o ayuda" (opcional)
            }"""
            
            # Obtener interpretación de la IA
            ai_response = await self.ai_service.process_message(
                command,
                system_message=system_message,
                context=context
            )
            
            # Procesar la respuesta de la IA
            try:
                interpretation = json.loads(ai_response)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500,
                    detail="Error al interpretar la respuesta de la IA"
                )
            
            # Ejecutar la operación correspondiente
            if interpretation["tipo"] == "LISTAR":
                result = await self.db_service.list_tables()
                return {
                    "status": "success",
                    "data": result,
                    "message": "Tablas listadas exitosamente"
                }
                
            elif interpretation["tipo"] == "MOSTRAR":
                if not interpretation.get("tabla"):
                    raise HTTPException(
                        status_code=400,
                        detail="No se especificó la tabla a mostrar"
                    )
                result = await self.db_service.get_table_content(interpretation["tabla"])
                return {
                    "status": "success",
                    "data": result,
                    "message": f"Contenido de la tabla {interpretation['tabla']} obtenido exitosamente"
                }
                
            elif interpretation["tipo"] == "CONSULTAR":
                if not interpretation.get("sql"):
                    raise HTTPException(
                        status_code=400,
                        detail="No se especificó la consulta SQL"
                    )
                result = await self.db_service.execute_query(interpretation["sql"])
                return {
                    "status": "success",
                    "data": result,
                    "message": "Consulta ejecutada exitosamente"
                }
                
            elif interpretation["tipo"] == "AYUDAR":
                return {
                    "status": "success",
                    "data": None,
                    "message": """Comandos MCP disponibles:
                    - LISTAR TABLAS: Muestra todas las tablas disponibles
                    - MOSTRAR <tabla>: Muestra el contenido de una tabla específica
                    - CONSULTAR <sql>: Ejecuta una consulta SQL personalizada
                    - AYUDAR: Muestra esta ayuda"""
                }
                
            else:
                raise HTTPException(
                    status_code=400,
                    detail=interpretation.get("mensaje", "Comando no reconocido")
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error en MCPService.execute_command: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del servidor: {str(e)}"
            )
            
    async def get_help(self) -> Dict[str, Any]:
        """Obtiene la ayuda del servicio MCP"""
        return {
            "status": "success",
            "data": {
                "comandos": [
                    {
                        "nombre": "LISTAR TABLAS",
                        "descripcion": "Muestra todas las tablas disponibles en la base de datos"
                    },
                    {
                        "nombre": "MOSTRAR <tabla>",
                        "descripcion": "Muestra el contenido de una tabla específica"
                    },
                    {
                        "nombre": "CONSULTAR <sql>",
                        "descripcion": "Ejecuta una consulta SQL personalizada"
                    },
                    {
                        "nombre": "AYUDAR",
                        "descripcion": "Muestra esta ayuda"
                    }
                ]
            },
            "message": "Ayuda del servicio MCP"
        }

# Instancia global del servicio MCP
mcp_service = MCPService() 