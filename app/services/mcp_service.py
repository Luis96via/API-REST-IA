import os
from typing import Dict, Any, AsyncIterator, Callable, List
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
from app.services.db_service import db_service
from app.exceptions import DatabaseError, TableNotFoundError, QueryError, ValidationError

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
    
    async def execute_mcp_command(self, action: str, **kwargs):
        """
        Ejecuta un comando MCP usando el servicio de base de datos.
        
        Args:
            action (str): La acción a ejecutar (list_tables, describe_table, execute_query, get_table_content)
            **kwargs: Argumentos adicionales según la acción
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            if action == "list_tables":
                return await db_service.list_tables()
                
            elif action == "describe_table":
                if not kwargs.get("table_name"):
                    raise ValidationError("Se requiere el parámetro 'table_name'")
                return await db_service.get_table_structure(kwargs["table_name"])
                
            elif action == "execute_query":
                if not kwargs.get("query"):
                    raise ValidationError("Se requiere el parámetro 'query'")
                return await db_service.execute_query(kwargs["query"])
                
            elif action == "get_table_content":
                if not kwargs.get("table_name"):
                    raise ValidationError("Se requiere el parámetro 'table_name'")
                return await db_service.get_table_content(
                    table_name=kwargs["table_name"],
                    limit=kwargs.get("limit"),
                    offset=kwargs.get("offset"),
                    order_by=kwargs.get("order_by"),
                    order_direction=kwargs.get("order_direction")
                )
                
            else:
                raise ValidationError(f"Acción no válida: {action}")
                
        except (DatabaseError, TableNotFoundError, QueryError, ValidationError) as e:
            raise e
        except Exception as e:
            raise DatabaseError(f"Error inesperado: {str(e)}")

# Instancia global del servicio MCP
mcp_service = MCPService() 