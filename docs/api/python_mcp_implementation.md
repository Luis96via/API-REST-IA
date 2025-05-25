# Implementación de MCP en Python

## Introducción
Esta guía detalla la implementación de servidores MCP (Machine Conversation Protocol) en Python utilizando el SDK oficial de MCP, siguiendo las mejores prácticas y especificaciones del protocolo.

## Requisitos Previos

### Dependencias Principales
```python
# requirements.txt
mcp[cli]>=1.0.0  # SDK oficial de MCP
fastapi>=0.109.2
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.26.0
```

## Estructura del Proyecto
```
mcp_server/
├── __init__.py
├── server.py          # Configuración principal del servidor MCP
├── resources/         # Recursos MCP
│   ├── __init__.py
│   ├── database.py
│   └── files.py
├── tools/            # Herramientas MCP
│   ├── __init__.py
│   ├── database.py
│   └── analysis.py
├── prompts/          # Plantillas de prompts
│   ├── __init__.py
│   └── templates.py
└── config.py         # Configuración general
```

## Implementación Base

### 1. Configuración del Servidor
```python
# server.py
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP, Context

# Crear servidor MCP con nombre
mcp = FastMCP("Mi Servidor MCP")

# Configurar dependencias
mcp = FastMCP(
    "Mi Servidor MCP",
    dependencies=["pandas", "numpy"],
    stateless_http=True  # Para mejor escalabilidad
)

@dataclass
class AppContext:
    """Contexto de la aplicación"""
    db: Database
    cache: Cache

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Gestión del ciclo de vida de la aplicación"""
    # Inicialización al arrancar
    db = await Database.connect()
    cache = await Cache.connect()
    try:
        yield AppContext(db=db, cache=cache)
    finally:
        # Limpieza al cerrar
        await db.disconnect()
        await cache.disconnect()

# Configurar servidor con ciclo de vida
mcp = FastMCP(
    "Mi Servidor MCP",
    lifespan=app_lifespan,
    stateless_http=True
)
```

### 2. Implementación de Recursos
```python
# resources/database.py
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Mi Servidor MCP")

@mcp.resource("database://schema/{table}")
async def get_table_schema(table: str, ctx: Context) -> str:
    """Obtener esquema de una tabla"""
    db = ctx.request_context.lifespan_context.db
    schema = await db.get_table_schema(table)
    return schema

@mcp.resource("database://stats")
async def get_database_stats(ctx: Context) -> str:
    """Obtener estadísticas de la base de datos"""
    db = ctx.request_context.lifespan_context.db
    stats = await db.get_stats()
    return stats
```

### 3. Implementación de Herramientas
```python
# tools/database.py
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Mi Servidor MCP")

@mcp.tool()
async def execute_query(
    query: str,
    timeout: int = 30,
    ctx: Context
) -> str:
    """Ejecutar consulta SQL de forma segura"""
    db = ctx.request_context.lifespan_context.db
    
    # Validar consulta
    if not is_safe_query(query):
        raise ValueError("Consulta SQL no permitida")
    
    try:
        result = await db.execute(query, timeout=timeout)
        return str(result)
    except Exception as e:
        ctx.error(f"Error en consulta: {str(e)}")
        raise

@mcp.tool()
async def analyze_table(
    table: str,
    ctx: Context
) -> dict:
    """Analizar estructura y estadísticas de una tabla"""
    db = ctx.request_context.lifespan_context.db
    cache = ctx.request_context.lifespan_context.cache
    
    # Intentar obtener del caché
    cache_key = f"table_analysis:{table}"
    if cached := await cache.get(cache_key):
        return cached
    
    analysis = await db.analyze_table(table)
    await cache.set(cache_key, analysis, ttl=3600)
    return analysis
```

### 4. Implementación de Prompts
```python
# prompts/templates.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("Mi Servidor MCP")

@mcp.prompt()
def analyze_database() -> list[base.Message]:
    """Prompt para análisis de base de datos"""
    return [
        base.UserMessage("Analiza la estructura de la base de datos:"),
        base.AssistantMessage("Voy a analizar la base de datos. ¿Qué aspectos específicos te interesan?"),
        base.UserMessage("Necesito entender las relaciones entre tablas y el rendimiento."),
        base.AssistantMessage("Entendido. Usaré las herramientas de análisis para examinar la estructura y el rendimiento.")
    ]

@mcp.prompt()
def optimize_query(query: str) -> str:
    """Prompt para optimización de consultas"""
    return f"""Analiza y optimiza la siguiente consulta SQL:
    
    {query}
    
    Considera:
    1. Uso de índices
    2. Joins eficientes
    3. Filtros apropiados
    4. Rendimiento general
    """
```

### 5. Integración con FastAPI
```python
# main.py
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import contextlib

# Crear servidores MCP
db_mcp = FastMCP("Database Server", stateless_http=True)
analysis_mcp = FastMCP("Analysis Server", stateless_http=True)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación FastAPI"""
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(db_mcp.session_manager.run())
        await stack.enter_async_context(analysis_mcp.session_manager.run())
        yield

# Crear aplicación FastAPI
app = FastAPI(lifespan=lifespan)

# Montar servidores MCP
app.mount("/db", db_mcp.streamable_http_app())
app.mount("/analysis", analysis_mcp.streamable_http_app())
```

## Ejemplos de Uso

### 1. Ejecución en Desarrollo
```bash
# Ejecutar servidor en modo desarrollo
mcp dev server.py

# Ejecutar con dependencias adicionales
mcp dev server.py --with pandas --with numpy

# Montar código local
mcp dev server.py --with-editable .
```

### 2. Instalación en Claude Desktop
```bash
# Instalar servidor
mcp install server.py

# Instalar con nombre personalizado
mcp install server.py --name "Mi Servidor de Análisis"

# Instalar con variables de entorno
mcp install server.py -v API_KEY=abc123 -v DB_URL=postgres://...
```

### 3. Uso del Cliente MCP
```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    # Conectar al servidor MCP
    async with streamablehttp_client("http://localhost:8000/db") as (read, write, _):
        async with ClientSession(read, write) as session:
            # Inicializar conexión
            await session.initialize()
            
            # Listar recursos disponibles
            resources = await session.list_resources()
            
            # Listar herramientas disponibles
            tools = await session.list_tools()
            
            # Ejecutar consulta
            result = await session.call_tool(
                "execute_query",
                arguments={"query": "SELECT * FROM users LIMIT 10"}
            )
            print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Mejores Prácticas

### 1. Seguridad
- Implementar validación de consultas SQL
- Usar autenticación OAuth cuando sea necesario
- Limitar acceso a recursos sensibles
- Implementar rate limiting
- Sanitizar todas las entradas

### 2. Rendimiento
- Usar caché para recursos frecuentes
- Implementar timeouts en operaciones largas
- Usar servidores stateless para mejor escalabilidad
- Optimizar consultas de base de datos
- Implementar circuit breakers

### 3. Mantenimiento
- Documentar todos los recursos y herramientas
- Implementar logging estructurado
- Mantener métricas de uso
- Realizar pruebas regulares
- Actualizar dependencias

## Recursos

### Documentación Oficial
- [MCP Specification](https://mcp-spec.ejemplo.com)
- [Python MCP SDK](https://docs.ejemplo.com/python-mcp)
- [FastAPI Integration](https://fastapi.tiangolo.com/advanced/mcp/)

### Herramientas Recomendadas
- [MCP CLI](https://docs.ejemplo.com/mcp-cli)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)

### Contacto
Para soporte con MCP:
- Email: mcp-support@ejemplo.com
- Slack: #mcp-python
- GitHub: https://github.com/ejemplo/python-mcp 