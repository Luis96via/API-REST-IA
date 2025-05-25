# Documentación API REST con MCP

## Índice
1. [Introducción](#introducción)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Configuración](#configuración)
4. [API Endpoints](#api-endpoints)
5. [Base de Datos](#base-de-datos)
6. [MCP Integration](#mcp-integration)
7. [Desarrollo](#desarrollo)
8. [Despliegue](#despliegue)

## Introducción
Esta API REST integra modelos de lenguaje con el protocolo MCP para ejecutar tareas específicas, principalmente operaciones con base de datos PostgreSQL.

### Tecnologías Principales
- FastAPI: Framework web moderno y rápido
- MCP: Protocolo de conversación con máquinas
- PostgreSQL: Base de datos relacional
- OpenRouter: API para modelos de lenguaje
- Python Async/Await: Programación asíncrona

## Estructura del Proyecto
```
API_REST_PYTHON_MCP/
├── app/
│   ├── main.py           # Punto de entrada de la aplicación
│   ├── models.py         # Modelos Pydantic
│   └── services/
│       ├── ai_service.py # Servicio de IA
│       └── mcp_service.py # Servicio MCP
├── docs/                 # Documentación
├── tests/               # Tests
├── .env                 # Variables de entorno
└── requirements.txt     # Dependencias
```

## Configuración
Ver [CONFIGURATION.md](./CONFIGURATION.md) para detalles sobre:
- Variables de entorno
- Configuración de la base de datos
- Configuración de OpenRouter
- Configuración de MCP

## API Endpoints
Ver [api/endpoints.md](./api/endpoints.md) para documentación detallada de:
- `/chat`: Procesamiento de mensajes
- `/health`: Estado de la API
- `/test-config`: Configuración de OpenRouter
- `/mcp`: Servidor MCP

## Base de Datos
Ver [database/schema.md](./database/schema.md) para:
- Esquema de la base de datos
- Consultas comunes
- Migraciones

## MCP Integration
Ver [api/mcp.md](./api/mcp.md) para:
- Configuración del servidor MCP
- Herramientas disponibles
- Ejemplos de uso

## Desarrollo
Ver [DEVELOPMENT.md](./DEVELOPMENT.md) para:
- Configuración del entorno
- Guías de estilo
- Testing
- Mejores prácticas

## Despliegue
Ver [DEPLOYMENT.md](./DEPLOYMENT.md) para:
- Requisitos del sistema
- Pasos de despliegue
- Monitoreo
- Mantenimiento 