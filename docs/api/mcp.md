# Integración con MCP

## Introducción
MCP (Machine Conversation Protocol) es un protocolo que permite a los modelos de lenguaje interactuar con herramientas y servicios externos. En este proyecto, lo usamos para operaciones con la base de datos PostgreSQL.

## Configuración

### Inicialización
```python
from mcp.server.fastmcp import FastMCP, Context

class MCPService:
    def __init__(self):
        self.mcp = FastMCP(
            "PostgreSQL MCP Server",
            lifespan=app_lifespan,
            stateless_http=True
        )
```

### Ciclo de Vida
```python
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    context = AppContext(
        db_connection_string=os.getenv("SUPABASE_DB_URL")
    )
    try:
        yield context
    finally:
        pass
```

## Herramientas Disponibles

### 1. List Tables
Lista todas las tablas en la base de datos.

```python
@mcp.tool()
async def list_tables(ctx: Context) -> list[str]:
    """Lista todas las tablas en la base de datos"""
    ctx.info("Obteniendo lista de tablas...")
    with self._get_db_connection(ctx) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row['table_name'] for row in cur.fetchall()]
            ctx.info(f"Se encontraron {len(tables)} tablas")
            return tables
```

### 2. Describe Table
Describe la estructura de una tabla específica.

```python
@mcp.tool()
async def describe_table(ctx: Context, table_name: str) -> Dict[str, Any]:
    """Describe la estructura de una tabla"""
    ctx.info(f"Describiendo tabla: {table_name}")
    with self._get_db_connection(ctx) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
            """, (table_name,))
            columns = [dict(row) for row in cur.fetchall()]
            ctx.info(f"La tabla {table_name} tiene {len(columns)} columnas")
            return {'columns': columns}
```

### 3. Execute Query
Ejecuta una consulta SQL y devuelve los resultados.

```python
@mcp.tool()
async def execute_query(ctx: Context, query: str) -> Dict[str, Any]:
    """Ejecuta una consulta SQL y devuelve los resultados"""
    ctx.info("Ejecutando consulta SQL...")
    with self._get_db_connection(ctx) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            results = [dict(row) for row in cur.fetchall()]
            ctx.info(f"Consulta ejecutada, se obtuvieron {len(results)} resultados")
            return {'results': results}
```

## Uso con el Modelo de Lenguaje

### Integración con Chat
```python
async def process_chat(self, messages: List[ChatMessage], model: str = None) -> ChatResponse:
    # Determinar si necesitamos usar herramientas
    last_message = messages[-1].content.lower()
    needs_tools = any(keyword in last_message for keyword in [
        "base de datos", "tabla", "query", "sql", "select", "insert", "update", "delete"
    ])

    # Incluir herramientas si son necesarias
    if needs_tools:
        params["tools"] = self.tools
        params["tool_choice"] = "auto"
```

### Ejemplo de Interacción
```python
# Mensaje del usuario
"¿Qué tablas hay en la base de datos?"

# El modelo decide usar MCP
{
    "tool_calls": [{
        "function": {
            "name": "execute_mcp_command",
            "arguments": {
                "server_name": "postgres",
                "action": "list_tables"
            }
        }
    }]
}

# Respuesta del modelo
"En la base de datos hay las siguientes tablas: usuarios, productos, pedidos..."
```

## Mejores Prácticas

### 1. Manejo de Errores
```python
try:
    result = await self.mcp.tools["list_tables"]()
except Exception as e:
    ctx.error(f"Error al listar tablas: {str(e)}")
    raise
```

### 2. Logging
```python
ctx.info("Iniciando operación...")
ctx.warning("Advertencia: tabla no encontrada")
ctx.error("Error en la operación")
```

### 3. Seguridad
- Validar todas las entradas
- Sanitizar consultas SQL
- Usar parámetros en lugar de concatenación
- Limitar permisos de base de datos

### 4. Performance
- Usar conexiones eficientemente
- Implementar timeouts
- Cachear resultados cuando sea posible
- Optimizar consultas

## Ejemplos Completos

### Ejemplo 1: Listar Tablas
```python
# Usando el endpoint de chat
POST /chat
{
    "messages": [
        {
            "role": "user",
            "content": "¿Qué tablas hay en la base de datos?"
        }
    ]
}

# El modelo usa MCP
{
    "content": "En la base de datos hay las siguientes tablas: usuarios, productos, pedidos...",
    "model": "openai/gpt-3.5-turbo-1106",
    "usage": {
        "prompt_tokens": 14,
        "completion_tokens": 15,
        "total_tokens": 29
    }
}
```

### Ejemplo 2: Describir Tabla
```python
# Usando el endpoint de chat
POST /chat
{
    "messages": [
        {
            "role": "user",
            "content": "Describe la estructura de la tabla usuarios"
        }
    ]
}

# El modelo usa MCP
{
    "content": "La tabla usuarios tiene las siguientes columnas: id (integer), nombre (varchar), email (varchar)...",
    "model": "openai/gpt-3.5-turbo-1106",
    "usage": {
        "prompt_tokens": 20,
        "completion_tokens": 25,
        "total_tokens": 45
    }
}
```

## Troubleshooting

### Problemas Comunes

1. **Error de Conexión**
   ```python
   # Verificar la URL de conexión
   print(f"DB URL: {os.getenv('SUPABASE_DB_URL')}")
   ```

2. **Error de Permisos**
   ```python
   # Verificar permisos de la base de datos
   cur.execute("SELECT current_user, current_database()")
   ```

3. **Error de Timeout**
   ```python
   # Ajustar timeout de conexión
   conn = psycopg2.connect(
       db_connection_string,
       connect_timeout=10
   )
   ```

### Logging y Depuración
```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)
``` 