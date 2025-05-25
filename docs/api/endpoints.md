# Documentación de Endpoints

## Endpoints Disponibles

### 1. Chat (`POST /chat`)
Procesa mensajes de chat y obtiene respuestas del modelo de lenguaje.

#### Request
```json
{
    "messages": [
        {
            "role": "user",
            "content": "¿Qué tablas hay en la base de datos?"
        }
    ],
    "model": "openai/gpt-3.5-turbo-1106",
    "temperature": 0.7,
    "max_tokens": 1000
}
```

#### Response
```json
{
    "content": "En la base de datos hay las siguientes tablas: ...",
    "model": "openai/gpt-3.5-turbo-1106",
    "usage": {
        "prompt_tokens": 14,
        "completion_tokens": 15,
        "total_tokens": 29
    }
}
```

#### Códigos de Estado
- `200 OK`: Solicitud exitosa
- `500 Internal Server Error`: Error en el procesamiento

### 2. Health Check (`GET /health`)
Verifica el estado de la API y los servicios MCP.

#### Response
```json
{
    "status": "ok",
    "message": "API funcionando correctamente",
    "model": "openai/gpt-3.5-turbo-1106",
    "mcp_server": {
        "status": "running",
        "mount_path": "/mcp",
        "transport": "streamable-http"
    },
    "env_vars_loaded": {
        "SUPABASE_DB_URL": true,
        "OPENAI_API_KEY": true,
        "OPENAI_BASE_URL": true
    }
}
```

#### Códigos de Estado
- `200 OK`: API funcionando correctamente
- `503 Service Unavailable`: Servicio no disponible

### 3. Test Config (`GET /test-config`)
Verifica la configuración de OpenRouter.

#### Response
```json
{
    "openrouter_config": {
        "api_key_exists": true,
        "api_key_length": 73,
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-3.5-turbo-1106",
        "site_url": "http://localhost:8000",
        "site_name": "API-REST-MCP"
    }
}
```

#### Códigos de Estado
- `200 OK`: Configuración verificada
- `500 Internal Server Error`: Error en la verificación

### 4. MCP Server (`/mcp`)
Servidor MCP montado para operaciones con la base de datos.

#### Herramientas Disponibles

1. **List Tables**
   ```python
   @mcp.tool()
   async def list_tables(ctx: Context) -> list[str]
   ```
   Lista todas las tablas en la base de datos.

2. **Describe Table**
   ```python
   @mcp.tool()
   async def describe_table(ctx: Context, table_name: str) -> Dict[str, Any]
   ```
   Describe la estructura de una tabla específica.

3. **Execute Query**
   ```python
   @mcp.tool()
   async def execute_query(ctx: Context, query: str) -> Dict[str, Any]
   ```
   Ejecuta una consulta SQL y devuelve los resultados.

## Ejemplos de Uso

### Ejemplo 1: Consulta de Tablas
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

# Usando MCP directamente
POST /mcp
{
    "action": "list_tables"
}
```

### Ejemplo 2: Descripción de Tabla
```python
# Usando el endpoint de chat
POST /chat
{
    "messages": [
        {
            "role": "user",
            "content": "Describe la tabla usuarios"
        }
    ]
}

# Usando MCP directamente
POST /mcp
{
    "action": "describe_table",
    "params": {
        "table_name": "usuarios"
    }
}
```

### Ejemplo 3: Ejecutar Consulta
```python
# Usando el endpoint de chat
POST /chat
{
    "messages": [
        {
            "role": "user",
            "content": "Muestra los últimos 5 usuarios registrados"
        }
    ]
}

# Usando MCP directamente
POST /mcp
{
    "action": "execute_query",
    "params": {
        "query": "SELECT * FROM usuarios ORDER BY created_at DESC LIMIT 5"
    }
}
```

## Mejores Prácticas

1. **Manejo de Errores**
   - Siempre verificar los códigos de estado
   - Manejar errores de red
   - Validar respuestas

2. **Rate Limiting**
   - Respetar límites de la API
   - Implementar backoff exponencial
   - Cachear respuestas cuando sea posible

3. **Seguridad**
   - Usar HTTPS
   - Validar todas las entradas
   - Sanitizar consultas SQL
   - Proteger endpoints sensibles

4. **Performance**
   - Minimizar el tamaño de las respuestas
   - Usar paginación cuando sea necesario
   - Optimizar consultas a la base de datos 