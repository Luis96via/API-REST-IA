# 🚀 API-REST-MCP: Plataforma de Integración con IA

## 👨‍💻 Desarrollado por Luis Viña

### 📝 Descripción
API REST moderna y escalable desarrollada como base para un sistema avanzado de integración con modelos de lenguaje e inteligencia artificial. Este proyecto implementa una arquitectura modular que sienta las bases para la implementación del protocolo MCP (Model-Controller-Protocol) y la integración de Function Calling con agentes inteligentes.

### 🌟 Características Principales
- Arquitectura modular y extensible
- Integración con modelos de lenguaje a través de OpenRouter
- Sistema de chat asíncrono
- Implementación de agentes inteligentes
- Protocolo MCP para gestión de tareas
- API REST moderna con FastAPI
- Documentación automática con Swagger/OpenAPI
- Integración con bases de datos PostgreSQL
- Sistema de caché con Redis
- Manejo asíncrono de operaciones

### 🛠️ Stack Tecnológico
#### Backend
- **Framework Principal**: FastAPI 0.109.2
- **Protocolo MCP**: mcp[cli] 1.9.1
- **Base de Datos**: PostgreSQL con SQLAlchemy 2.0.0
- **Caché**: Redis 5.0.0
- **Autenticación**: JWT y OAuth2
- **Documentación**: Swagger/OpenAPI

#### Integración con IA
- **OpenAI**: openai 1.12.0
- **OpenRouter API**: Integración para modelos de lenguaje
- **Async/Await**: Operaciones asíncronas
- **HTTP Client**: httpx 0.26.0

#### Herramientas de Desarrollo
- **Testing**: pytest 8.0.0, pytest-asyncio, pytest-cov
- **Linting**: flake8 7.0.0, black 24.1.1, isort 5.13.2
- **Type Checking**: mypy 1.8.0
- **Load Testing**: locust 2.24.0

### 🚀 Instalación
```bash
# Clonar el repositorio
git clone https://github.com/luisvina/API-REST-MCP.git

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar la aplicación
uvicorn app.main:app --reload
```

### 📚 Documentación
La documentación completa de la API está disponible en `/docs` cuando el servidor está en ejecución.

### 🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviarnos pull requests.

### 📝 Licencia
Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.

### 👨‍💻 Autor
- **Luis Viña** - *Desarrollo inicial y mantenimiento* - [GitHub](https://github.com/luisvina)

### 🙏 Agradecimientos
- OpenRouter por proporcionar acceso a modelos de lenguaje
- La comunidad de FastAPI por su excelente documentación
- Todos los contribuidores que han ayudado a mejorar este proyecto

### 📊 Métricas del Proyecto
- **Versión Actual**: 1.0.0
- **Última Actualización**: Marzo 2024
- **Estado**: En desarrollo activo 