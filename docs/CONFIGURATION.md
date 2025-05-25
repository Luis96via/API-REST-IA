# Configuración del Proyecto

## Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# OpenRouter
OPENAI_API_KEY=sk-or-...        # Tu API key de OpenRouter
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=openai/gpt-3.5-turbo-1106
SITE_URL=http://localhost:8000  # URL de tu sitio
SITE_NAME=API-REST-MCP          # Nombre de tu aplicación

# Base de Datos
SUPABASE_DB_URL=postgresql://... # URL de conexión a PostgreSQL

# MCP
MCP_HOST=localhost
MCP_PORT=3000
```

## Configuración de FastAPI
La aplicación FastAPI está configurada en `app/main.py`:

```python
app = FastAPI(
    title="API Chat con OpenRouter y MCP",
    description="API REST que integra modelos de lenguaje con el protocolo MCP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

## Configuración de MCP
El servidor MCP está configurado en `app/services/mcp_service.py`:

```python
self.mcp = FastMCP(
    "PostgreSQL MCP Server",
    lifespan=app_lifespan,
    stateless_http=True
)
```

## Configuración de la Base de Datos
La conexión a PostgreSQL se maneja a través de psycopg2:

```python
conn = psycopg2.connect(
    db_connection_string,
    cursor_factory=RealDictCursor
)
```

## Configuración de CORS
CORS está configurado para desarrollo local:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Configuración de Logging
El logging se maneja a través de los métodos `ctx.info()` de MCP y print statements.

## Configuración de Testing
Los tests están configurados en el directorio `tests/`:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
```

## Configuración de Desarrollo
Herramientas de desarrollo configuradas:

- **black**: Formateador de código
- **isort**: Organizador de imports
- **flake8**: Linter
- **mypy**: Verificador de tipos
- **pytest**: Framework de testing

## Configuración de Producción
Para producción, considerar:

1. Configurar CORS adecuadamente
2. Usar variables de entorno seguras
3. Configurar logging apropiado
4. Implementar rate limiting
5. Configurar SSL/TLS
6. Implementar autenticación

## Monitoreo
Considerar implementar:

1. Health checks
2. Métricas de rendimiento
3. Logging estructurado
4. Alertas

## Seguridad
Mejores prácticas de seguridad:

1. Nunca exponer API keys
2. Usar HTTPS en producción
3. Implementar rate limiting
4. Validar todas las entradas
5. Mantener dependencias actualizadas
6. Usar secrets management 