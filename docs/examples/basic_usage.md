# Ejemplos Básicos de Uso

## Introducción
Este documento proporciona ejemplos básicos de cómo usar la API REST con MCP. Los ejemplos están organizados por funcionalidad y muestran casos de uso comunes.

## Autenticación

### 1. Registro de Usuario
```python
import httpx

async def register_user():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ejemplo.com/auth/register",
            json={
                "nombre": "Usuario Ejemplo",
                "email": "usuario@ejemplo.com",
                "password": "Contraseña123!"
            }
        )
        return response.json()

# Uso
user = await register_user()
print(f"Usuario registrado: {user['nombre']}")
```

### 2. Login
```python
async def login():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ejemplo.com/auth/login",
            json={
                "email": "usuario@ejemplo.com",
                "password": "Contraseña123!"
            }
        )
        return response.json()

# Uso
auth = await login()
token = auth["access_token"]
```

## Chat con MCP

### 1. Consulta Simple
```python
async def chat_query(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ejemplo.com/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": "¿Qué tablas hay en la base de datos?"
                    }
                ]
            }
        )
        return response.json()

# Uso
auth = await login()
response = await chat_query(auth["access_token"])
print(f"Respuesta: {response['content']}")
```

### 2. Consulta con Contexto
```python
async def chat_with_context(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ejemplo.com/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en bases de datos."
                    },
                    {
                        "role": "user",
                        "content": "Describe la tabla usuarios"
                    }
                ]
            }
        )
        return response.json()

# Uso
response = await chat_with_context(token)
print(f"Descripción: {response['content']}")
```

## Operaciones con Base de Datos

### 1. Listar Tablas
```python
async def list_tables(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ejemplo.com/mcp",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action": "list_tables"
            }
        )
        return response.json()

# Uso
tables = await list_tables(token)
print(f"Tablas disponibles: {tables}")
```

### 2. Describir Tabla
```python
async def describe_table(token: str, table_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ejemplo.com/mcp",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action": "describe_table",
                "params": {
                    "table_name": table_name
                }
            }
        )
        return response.json()

# Uso
table_info = await describe_table(token, "usuarios")
print(f"Estructura de la tabla: {table_info}")
```

### 3. Ejecutar Consulta
```python
async def execute_query(token: str, query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.ejemplo.com/mcp",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action": "execute_query",
                "params": {
                    "query": query
                }
            }
        )
        return response.json()

# Uso
query = "SELECT * FROM usuarios LIMIT 5"
results = await execute_query(token, query)
print(f"Resultados: {results}")
```

## Manejo de Errores

### 1. Try/Except Básico
```python
async def safe_api_call(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except httpx.HTTPStatusError as e:
        print(f"Error HTTP: {e.response.status_code}")
        print(f"Detalles: {e.response.json()}")
    except httpx.RequestError as e:
        print(f"Error de conexión: {str(e)}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

# Uso
await safe_api_call(chat_query, token)
```

### 2. Retry con Backoff
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def reliable_api_call(func, *args, **kwargs):
    return await func(*args, **kwargs)

# Uso
try:
    result = await reliable_api_call(chat_query, token)
    print(f"Resultado: {result}")
except Exception as e:
    print(f"Error después de reintentos: {str(e)}")
```

## Ejemplos Completos

### 1. Cliente API
```python
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.client = httpx.AsyncClient()

    async def login(self, email: str, password: str):
        response = await self.client.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data["access_token"]
        return data

    async def chat(self, message: str):
        if not self.token:
            raise ValueError("No hay token de autenticación")
        
        response = await self.client.post(
            f"{self.base_url}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"messages": [{"role": "user", "content": message}]}
        )
        return response.json()

    async def close(self):
        await self.client.aclose()

# Uso
async def main():
    client = APIClient("https://api.ejemplo.com")
    try:
        await client.login("usuario@ejemplo.com", "Contraseña123!")
        response = await client.chat("¿Qué tablas hay?")
        print(f"Respuesta: {response['content']}")
    finally:
        await client.close()

# Ejecutar
asyncio.run(main())
```

### 2. Script de Monitoreo
```python
import asyncio
import time
from datetime import datetime

class APIMonitor:
    def __init__(self, client: APIClient):
        self.client = client
        self.results = []

    async def check_health(self):
        start = time.time()
        try:
            response = await self.client.chat("health check")
            latency = time.time() - start
            self.results.append({
                "timestamp": datetime.utcnow().isoformat(),
                "status": "ok",
                "latency": latency
            })
        except Exception as e:
            self.results.append({
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            })

    async def monitor(self, interval: int = 60, duration: int = 3600):
        end_time = time.time() + duration
        while time.time() < end_time:
            await self.check_health()
            await asyncio.sleep(interval)

    def generate_report(self):
        total = len(self.results)
        successful = sum(1 for r in self.results if r["status"] == "ok")
        avg_latency = sum(r["latency"] for r in self.results if "latency" in r) / successful
        
        return {
            "total_checks": total,
            "success_rate": successful / total * 100,
            "average_latency": avg_latency,
            "errors": [r for r in self.results if r["status"] == "error"]
        }

# Uso
async def monitor_api():
    client = APIClient("https://api.ejemplo.com")
    monitor = APIMonitor(client)
    try:
        await client.login("monitor@ejemplo.com", "Contraseña123!")
        await monitor.monitor(interval=60, duration=3600)
        report = monitor.generate_report()
        print(f"Reporte: {report}")
    finally:
        await client.close()

# Ejecutar
asyncio.run(monitor_api())
```

## Recursos Adicionales

### Documentación
- [Documentación de API](./api/endpoints.md)
- [Guía de Autenticación](./api/authentication.md)
- [Integración MCP](./api/mcp.md)

### Herramientas
- [httpx](https://www.python-httpx.org/)
- [tenacity](https://tenacity.readthedocs.io/)
- [asyncio](https://docs.python.org/3/library/asyncio.html)

### Ejemplos en GitHub
- [Ejemplos Básicos](https://github.com/tu-usuario/api-rest-mcp/examples)
- [Ejemplos Avanzados](https://github.com/tu-usuario/api-rest-mcp/examples/advanced)
- [Ejemplos de Testing](https://github.com/tu-usuario/api-rest-mcp/examples/testing) 