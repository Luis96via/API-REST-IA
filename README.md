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

## Despliegue en Render.com

### Requisitos Previos
1. Una cuenta en [Render.com](https://render.com)
2. Una cuenta en [OpenRouter](https://openrouter.ai) para la API key
3. Una cuenta en [Supabase](https://supabase.com) con una base de datos PostgreSQL configurada
4. Git instalado en tu sistema

### Pasos para el Despliegue

1. **Fork del Repositorio**
   - Haz fork de este repositorio a tu cuenta de GitHub

2. **Crear una Nueva Aplicación en Render**
   - Ve a [Render Dashboard](https://dashboard.render.com)
   - Haz clic en "New +" y selecciona "Blueprint"
   - Conecta tu repositorio de GitHub
   - Selecciona el repositorio forkeado

3. **Configurar Variables de Entorno**
   - En el dashboard de Render, ve a la sección "Environment"
   - Agrega las siguientes variables:
     - `OPENAI_API_KEY`: Tu API key de OpenRouter
     - `DATABASE_URL`: URL de conexión a tu base de datos Supabase
     - `SUPABASE_DB_URL`: URL de conexión a tu base de datos Supabase
     - `SUPABASE_ANON_KEY`: Tu clave anónima de Supabase
     - `SUPABASE_SERVICE_ROLE_KEY`: Tu clave de servicio de Supabase
     - `DEBUG`: "false" para producción
     - `MODEL_NAME`: "gpt-3.5-turbo-1106" (o el modelo que prefieras)
     - `OPENAI_BASE_URL`: "https://openrouter.ai/api/v1"
     - `CORS_ORIGINS`: "*" (ajusta según tus necesidades)
     - `SITE_URL`: URL de tu aplicación en Render
     - `SITE_NAME`: Nombre de tu aplicación

4. **Despliegue Automático**
   - Render detectará automáticamente el `render.yaml` y configurará:
     - Servicio web (API)
     - Servicio Redis
   - El despliegue comenzará automáticamente
   - La aplicación usará tu base de datos Supabase existente

5. **Verificar el Despliegue**
   - Una vez completado el despliegue, Render proporcionará una URL
   - Visita `{URL}/docs` para ver la documentación de la API
   - Prueba los endpoints para verificar que todo funcione correctamente
   - Verifica que la conexión a Supabase esté funcionando

### Estructura del Despliegue

El proyecto se despliega con dos servicios:

1. **API REST (Web Service)**
   - Construido con FastAPI
   - Expuesto en el puerto 8000
   - Incluye documentación Swagger en `/docs`
   - Conectado a tu base de datos Supabase existente

2. **Redis**
   - Plan gratuito de Render
   - Usado para caché y sesiones
   - Persistencia habilitada

### Base de Datos (Supabase)

La aplicación utiliza tu base de datos PostgreSQL existente en Supabase:
- Conexión segura con SSL
- Acceso mediante credenciales de Supabase
- Misma base de datos tanto en desarrollo como en producción
- Mantenimiento y backups gestionados por Supabase

### Monitoreo y Mantenimiento

- Render proporciona logs en tiempo real
- Monitoreo de salud automático en `/docs`
- Monitoreo de la base de datos a través del dashboard de Supabase
- Redis con política de persistencia

### Solución de Problemas

Si encuentras problemas durante el despliegue:

1. Revisa los logs en el dashboard de Render
2. Verifica que todas las variables de entorno estén configuradas
3. Asegúrate de que la API key de OpenRouter sea válida
4. Comprueba la conexión a Supabase en el dashboard de Supabase
5. Verifica que las credenciales de Supabase sean correctas
6. Asegúrate de que la base de datos de Supabase esté accesible desde Render 