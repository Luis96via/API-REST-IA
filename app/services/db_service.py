import os
from typing import Dict, Any, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
from app.exceptions import (
    DatabaseError,
    TableNotFoundError,
    QueryError,
    ConnectionError,
    ValidationError
)
from app.config import settings
import asyncpg
import logging
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        """Inicializa el servicio de base de datos"""
        self.pool = None
        self.db_url = settings.DATABASE_URL
        if not self.db_url:
            raise ConnectionError("No se encontró la URL de conexión a la base de datos (DATABASE_URL)")
        
        # Verificar la conexión al iniciar
        self._verify_connection()
    
    async def get_pool(self) -> asyncpg.Pool:
        """Obtiene o crea el pool de conexiones a la base de datos"""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    dsn=settings.DATABASE_URL,
                    min_size=1,
                    max_size=10
                )
            except Exception as e:
                logger.error(f"Error al crear el pool de conexiones: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error al conectar con la base de datos"
                )
        return self.pool
    
    def _get_connection_params(self) -> dict:
        """Obtiene los parámetros de conexión optimizados"""
        try:
            # Si la URL comienza con @, remover el @
            if self.db_url.startswith('@'):
                self.db_url = self.db_url[1:]
            
            # Si la URL no comienza con postgresql://, añadir el prefijo
            if not self.db_url.startswith('postgresql://'):
                self.db_url = f"postgresql://{self.db_url}"
            
            import urllib.parse
            parsed = urllib.parse.urlparse(self.db_url)
            
            return {
                'dbname': parsed.path[1:] or 'postgres',
                'user': parsed.username or 'postgres',
                'password': parsed.password,
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'cursor_factory': RealDictCursor,
                'connect_timeout': 60,
                'keepalives': 1,
                'keepalives_idle': 60,
                'keepalives_interval': 20,
                'keepalives_count': 5,
                'application_name': 'db_service',
                'options': '-c statement_timeout=60000 -c idle_in_transaction_session_timeout=60000',
                'sslmode': 'require'
            }
        except Exception as e:
            raise ConnectionError(f"Error al procesar la URL de conexión: {str(e)}")
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        try:
            return psycopg2.connect(**self._get_connection_params())
        except Exception as e:
            raise ConnectionError(f"Error al conectar a la base de datos: {str(e)}")
    
    def _verify_connection(self):
        """Verifica que la conexión a la base de datos funcione"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    version = cur.fetchone()
                    print(f"Conexión exitosa a PostgreSQL. Versión: {version['version']}")
        except Exception as e:
            raise ConnectionError(f"Error al verificar la conexión: {str(e)}")
    
    def _format_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formatea los resultados para hacerlos serializables a JSON"""
        formatted_results = []
        for row in results:
            formatted_row = {}
            for key, value in row.items():
                if isinstance(value, datetime.datetime):
                    formatted_row[key] = value.isoformat()
                else:
                    formatted_row[key] = value
            formatted_results.append(formatted_row)
        return formatted_results
    
    async def list_tables(self) -> List[str]:
        """Lista todas las tablas disponibles en la base de datos"""
        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                return [table['table_name'] for table in tables]
        except Exception as e:
            logger.error(f"Error al listar tablas: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error al obtener la lista de tablas"
            )
    
    async def get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Obtiene la estructura de una tabla específica"""
        try:
            # Verificar que la tabla existe
            if not await self._table_exists(table_name):
                raise TableNotFoundError(table_name)
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            column_name, 
                            data_type, 
                            character_maximum_length,
                            is_nullable,
                            column_default
                        FROM information_schema.columns
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                        ORDER BY ordinal_position;
                    """, (table_name,))
                    
                    columns = [
                        {
                            "name": row['column_name'],
                            "type": row['data_type'],
                            "max_length": row['character_maximum_length'],
                            "nullable": row['is_nullable'],
                            "default": row['column_default']
                        }
                        for row in cur.fetchall()
                    ]
                    
                    return {
                        "status": "success",
                        "table": table_name,
                        "columns": columns
                    }
        except TableNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Error al obtener estructura de la tabla: {str(e)}")
    
    async def get_table_content(
        self,
        table_name: str,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = "ASC"
    ) -> Dict[str, Any]:
        """
        Obtiene el contenido de una tabla específica
        
        Args:
            table_name: Nombre de la tabla
            limit: Límite de registros a obtener
            offset: Desplazamiento para paginación
            order_by: Columna por la que ordenar
            order_direction: Dirección del ordenamiento (ASC/DESC)
            
        Returns:
            Dict con los datos de la tabla y metadatos
        """
        try:
            # Validar parámetros
            if not table_name:
                raise HTTPException(
                    status_code=400,
                    detail="El nombre de la tabla es requerido"
                )
                
            if order_direction not in ["ASC", "DESC"]:
                order_direction = "ASC"
                
            # Construir la consulta
            query = f"SELECT * FROM {table_name}"
            if order_by:
                query += f" ORDER BY {order_by} {order_direction}"
            query += f" LIMIT {limit} OFFSET {offset}"
            
            # Ejecutar la consulta
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                # Obtener estructura de la tabla
                columns = await conn.fetch("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = $1
                """, table_name)
                
                if not columns:
                    raise HTTPException(
                        status_code=404,
                        detail=f"La tabla {table_name} no existe"
                    )
                    
                # Obtener datos
                rows = await conn.fetch(query)
                
                # Convertir a formato JSON
                data = [dict(row) for row in rows]
                structure = [dict(col) for col in columns]
                
                return {
                    "table_name": table_name,
                    "structure": structure,
                    "data": data,
                    "total": len(data),
                    "limit": limit,
                    "offset": offset
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al obtener contenido de la tabla {table_name}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener datos de la tabla {table_name}"
            )
    
    def _is_safe_query(self, query: str) -> bool:
        """
        Verifica si una consulta SQL es segura para ejecutar.
        Permite todas las operaciones SQL, incluyendo triggers y funciones.
        """
        # Convertir a minúsculas para la validación
        query_lower = query.lower().strip()
        
        # Lista de palabras clave extremadamente peligrosas que NO permitiremos
        dangerous_keywords = [
            'drop database', 'drop schema', 'alter database',
            'alter schema', 'create database', 'create schema',
            'drop role', 'create role', 'grant all', 'revoke all'
        ]
        
        # Verificar que no contenga palabras clave extremadamente peligrosas
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False
        
        # Permitir todas las operaciones SQL
        return True

    async def discover_tables(self) -> Dict[str, Any]:
        """
        Descubre dinámicamente todas las tablas en la base de datos y su información.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Obtener todas las tablas y su información
                    cur.execute("""
                        SELECT 
                            t.table_name,
                            t.table_type,
                            (SELECT COUNT(*) FROM information_schema.columns 
                             WHERE table_schema = 'public' 
                             AND table_name = t.table_name) as column_count,
                            (SELECT COUNT(*) FROM information_schema.table_constraints 
                             WHERE table_schema = 'public' 
                             AND table_name = t.table_name) as constraint_count
                        FROM information_schema.tables t
                        WHERE t.table_schema = 'public'
                        ORDER BY t.table_name;
                    """)
                    tables = cur.fetchall()
                    
                    # Obtener información detallada de cada tabla
                    detailed_tables = []
                    for table in tables:
                        # Obtener columnas
                        cur.execute("""
                            SELECT 
                                column_name,
                                data_type,
                                is_nullable,
                                column_default
                            FROM information_schema.columns
                            WHERE table_schema = 'public'
                            AND table_name = %s
                            ORDER BY ordinal_position;
                        """, (table['table_name'],))
                        columns = cur.fetchall()
                        
                        # Obtener restricciones
                        cur.execute("""
                            SELECT 
                                constraint_name,
                                constraint_type
                            FROM information_schema.table_constraints
                            WHERE table_schema = 'public'
                            AND table_name = %s;
                        """, (table['table_name'],))
                        constraints = cur.fetchall()
                        
                        detailed_tables.append({
                            "name": table['table_name'],
                            "type": table['table_type'],
                            "column_count": table['column_count'],
                            "constraint_count": table['constraint_count'],
                            "columns": columns,
                            "constraints": constraints
                        })
                    
                    return {
                        "status": "success",
                        "tables": detailed_tables,
                        "total_tables": len(detailed_tables)
                    }
        except Exception as e:
            raise DatabaseError(f"Error al descubrir tablas: {str(e)}")

    async def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Ejecuta una consulta SQL personalizada
        
        Args:
            query: Consulta SQL a ejecutar
            
        Returns:
            Dict con los resultados de la consulta
        """
        try:
            if not query:
                raise HTTPException(
                    status_code=400,
                    detail="La consulta SQL es requerida"
                )
                
            # Validar que la consulta sea de solo lectura
            query_lower = query.lower().strip()
            if any(keyword in query_lower for keyword in ["insert", "update", "delete", "drop", "alter", "create"]):
                raise HTTPException(
                    status_code=403,
                    detail="Solo se permiten consultas de lectura (SELECT)"
                )
                
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                try:
                    rows = await conn.fetch(query)
                    data = [dict(row) for row in rows]
                    return {
                        "status": "success",
                        "data": data,
                        "total": len(data)
                    }
                except asyncpg.exceptions.PostgresError as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error en la consulta SQL: {str(e)}"
                    )
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al ejecutar consulta: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error al ejecutar la consulta SQL"
            )
    
    async def _table_exists(self, table_name: str) -> bool:
        """Verifica si una tabla existe en la base de datos"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        );
                    """, (table_name,))
                    return cur.fetchone()['exists']
        except Exception as e:
            raise DatabaseError(f"Error al verificar existencia de la tabla: {str(e)}")

    async def close(self):
        """Cierra el pool de conexiones"""
        if self.pool:
            await self.pool.close()
            self.pool = None

# Instancia global del servicio de base de datos
db_service = DatabaseService() 