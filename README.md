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

### 📡 Endpoints Disponibles

#### 1. Interacción con Base de Datos
- **`POST /api/db/query`**
  - Ejecuta consultas SQL directamente
  - Ideal para operaciones SQL específicas
  - Requiere conocimiento de SQL

- **`GET /api/db/tables`**
  - Lista todas las tablas disponibles
  - Útil para explorar la estructura de la base de datos

- **`GET /api/db/tables/{table_name}`**
  - Obtiene el contenido de una tabla específica
  - Ejemplo: `/api/db/tables/usuarios`

- **`GET /api/db/tables/{table_name}/structure`**
  - Muestra la estructura y tipos de datos de una tabla
  - Útil para entender el esquema de la base de datos

#### 2. Interacción con IA
- **`POST /api/chat`**
  - Interfaz conversacional con IA
  - Permite consultas en lenguaje natural
  - Convierte preguntas en consultas SQL
  - Ideal para usuarios no técnicos

#### 3. Operaciones de Negocio
- **`POST /api/pedidos`**
  - Endpoint específico para gestión de pedidos
  - Maneja la lógica de negocio de pedidos
  - Estructura de datos optimizada

#### 4. Protocolo MCP
- **`POST /mcp`**
  - Endpoint para operaciones del Modelo de Control de Procesos
  - Permite operaciones complejas y automatizadas
  - Ideal para integración con otros sistemas

### 🔍 ¿Por qué múltiples endpoints?
1. **Diferentes niveles de abstracción**
   - `/chat` para usuarios finales
   - `/api/db/query` para desarrolladores
   - Endpoints específicos para operaciones comunes

2. **Casos de uso específicos**
   - Integración con otros sistemas
   - Automatización de procesos
   - Operaciones repetitivas
   - Respuestas rápidas y predecibles

3. **Rendimiento y control**
   - Endpoints específicos más rápidos que `/chat`
   - Validaciones y lógica de negocio incorporada
   - Mayor control sobre las operaciones

4. **Seguridad y mantenimiento**
   - Validaciones estrictas en endpoints específicos
   - Monitoreo y mantenimiento simplificado
   - Control granular de permisos

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