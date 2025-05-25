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

class DatabaseService:
    def __init__(self):
        """Inicializa el servicio de base de datos"""
        self.db_url = settings.DATABASE_URL
        if not self.db_url:
            raise ConnectionError("No se encontró la URL de conexión a la base de datos (DATABASE_URL)")
        
        # Verificar la conexión al iniciar
        self._verify_connection()
    
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
    
    async def list_tables(self) -> Dict[str, Any]:
        """Lista todas las tablas disponibles en la base de datos"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name;
                    """)
                    tables = [row['table_name'] for row in cur.fetchall()]
                    return {
                        "status": "success",
                        "tables": tables
                    }
        except Exception as e:
            raise DatabaseError(f"Error al listar tablas: {str(e)}")
    
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
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtiene el contenido de una tabla específica"""
        try:
            # Verificar que la tabla existe
            if not await self._table_exists(table_name):
                raise TableNotFoundError(table_name)
            
            # Construir la consulta base
            query = f"SELECT * FROM {table_name}"
            
            # Añadir ordenamiento si se especifica
            if order_by:
                direction = "DESC" if order_direction and order_direction.upper() == "DESC" else "ASC"
                query += f" ORDER BY {order_by} {direction}"
            
            # Añadir límite y offset si se especifican
            if limit is not None:
                query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Obtener datos
                    cur.execute(query)
                    results = self._format_results(cur.fetchall())
                    
                    # Obtener total de registros
                    cur.execute(f"SELECT COUNT(*) as total FROM {table_name}")
                    total = cur.fetchone()['total']
                    
                    # Obtener columnas
                    cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = %s 
                        ORDER BY ordinal_position;
                    """, (table_name,))
                    columns = [row['column_name'] for row in cur.fetchall()]
                    
                    return {
                        "status": "success",
                        "table": table_name,
                        "columns": columns,
                        "data": results,
                        "total": total,
                        "limit": limit,
                        "offset": offset
                    }
        except TableNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Error al obtener contenido de la tabla: {str(e)}")
    
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

    async def execute_query(self, query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Ejecuta una consulta SQL personalizada con validación de seguridad.
        Permite operaciones CRUD básicas.
        """
        try:
            # Validar que la consulta sea segura
            if not self._is_safe_query(query):
                raise ValidationError(
                    "La consulta no está permitida por razones de seguridad. " +
                    "Solo se permiten operaciones CRUD básicas (SELECT, INSERT, UPDATE, DELETE, CREATE TABLE, ALTER TABLE)."
                )
            
            print(f"Ejecutando consulta: {query}")  # Log para depuración
            
            # Si es una operación de modificación, verificar primero el estado actual
            if any(query.lower().strip().startswith(op) for op in ['alter table', 'drop table', 'rename table']):
                # Descubrir tablas antes de la operación
                tables_before = await self.discover_tables()
                print(f"Estado de tablas antes de la operación: {tables_before}")
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Ejecutar la consulta
                    cur.execute(query, params)
                    
                    # Si es una consulta SELECT, retornar los resultados
                    if query.lower().strip().startswith('select'):
                        results = self._format_results(cur.fetchall())
                        return {
                            "status": "success",
                            "results": results
                        }
                    
                    # Para operaciones de modificación
                    try:
                        conn.commit()
                        print(f"Cambios guardados exitosamente. Filas afectadas: {cur.rowcount}")
                        
                        # Si fue una operación de modificación, verificar el nuevo estado
                        if any(query.lower().strip().startswith(op) for op in ['alter table', 'drop table', 'rename table']):
                            tables_after = await self.discover_tables()
                            print(f"Estado de tablas después de la operación: {tables_after}")
                            
                            # Comparar estados para verificar cambios
                            if len(tables_after['tables']) != len(tables_before['tables']):
                                return {
                                    "status": "success",
                                    "message": "Operación completada. Se detectaron cambios en la estructura de las tablas.",
                                    "affected_rows": cur.rowcount,
                                    "tables_before": tables_before,
                                    "tables_after": tables_after
                                }
                        
                        return {
                            "status": "success",
                            "message": "Operación ejecutada correctamente",
                            "affected_rows": cur.rowcount
                        }
                    except Exception as commit_error:
                        print(f"Error al hacer commit: {str(commit_error)}")
                        conn.rollback()
                        raise DatabaseError(f"Error al guardar los cambios: {str(commit_error)}")
                    
        except Exception as e:
            if 'conn' in locals():
                try:
                    conn.rollback()
                    print(f"Rollback ejecutado debido a: {str(e)}")
                except Exception as rollback_error:
                    print(f"Error al hacer rollback: {str(rollback_error)}")
            raise QueryError(query, str(e))
    
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

# Instancia global del servicio de base de datos
db_service = DatabaseService() 