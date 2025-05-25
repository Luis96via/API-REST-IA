from typing import Optional

class DatabaseError(Exception):
    """Excepción base para errores de base de datos"""
    def __init__(self, message: str, code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class TableNotFoundError(DatabaseError):
    """Excepción para cuando una tabla no existe"""
    def __init__(self, table_name: str):
        super().__init__(
            message=f"La tabla '{table_name}' no existe",
            code=404,
            details={"table_name": table_name}
        )

class QueryError(DatabaseError):
    """Excepción para errores en consultas SQL"""
    def __init__(self, query: str, error: str):
        super().__init__(
            message=f"Error al ejecutar la consulta: {error}",
            code=400,
            details={"query": query, "error": error}
        )

class ConnectionError(DatabaseError):
    """Excepción para errores de conexión a la base de datos"""
    def __init__(self, error: str):
        super().__init__(
            message=f"Error de conexión a la base de datos: {error}",
            code=503,
            details={"error": error}
        )

class ValidationError(DatabaseError):
    """Excepción para errores de validación"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code=400,
            details=details
        ) 