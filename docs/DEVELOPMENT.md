# Guía de Desarrollo

## Introducción
Esta guía detalla los pasos para configurar el entorno de desarrollo, las mejores prácticas y los procesos de testing para la API REST con MCP.

## Configuración del Entorno

### Requisitos
- Python 3.9 o superior
- PostgreSQL 13 o superior
- Git

### Pasos de Instalación

1. **Clonar el Repositorio**
   ```bash
   git clone <url-del-repo>
   cd API_REST_PYTHON_MCP
   ```

2. **Crear Entorno Virtual**
   ```bash
   python -m venv venv
   # En Windows
   .\venv\Scripts\activate
   # En Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno**
   ```bash
   # Copiar el archivo de ejemplo
   cp .env.example .env
   # Editar .env con tus valores
   ```

### Estructura del Proyecto
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

## Guías de Estilo

### Python

1. **PEP 8**
   - Usar 4 espacios para indentación
   - Máximo 79 caracteres por línea
   - Docstrings en estilo Google
   - Nombres descriptivos

2. **Imports**
   ```python
   # Standard library
   import os
   import sys

   # Third-party
   import fastapi
   import pydantic

   # Local
   from app.services import ai_service
   ```

3. **Docstrings**
   ```python
   def process_chat(messages: List[ChatMessage], model: str = None) -> ChatResponse:
       """Procesa mensajes de chat y obtiene respuestas del modelo.

       Args:
           messages (List[ChatMessage]): Lista de mensajes a procesar.
           model (str, optional): Modelo a usar. Defaults to None.

       Returns:
           ChatResponse: Respuesta del modelo.

       Raises:
           ValueError: Si el modelo no es válido.
       """
   ```

### SQL

1. **Formato**
   ```sql
   -- Usar mayúsculas para palabras clave
   SELECT
       u.id,
       u.nombre,
       u.email
   FROM
       usuarios u
   WHERE
       u.email = %s
   ORDER BY
       u.created_at DESC;
   ```

2. **Nombres**
   - Tablas en plural
   - Columnas en singular
   - Índices descriptivos

## Testing

### Configuración

1. **Instalar Dependencias de Testing**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Configurar Base de Datos de Testing**
   ```bash
   # Crear base de datos de testing
   createdb api_test_db
   ```

### Escribir Tests

1. **Test de Endpoints**
   ```python
   # tests/test_chat.py
   def test_chat_endpoint(client):
       response = client.post(
           "/chat",
           json={
               "messages": [
                   {
                       "role": "user",
                       "content": "¿Qué tablas hay?"
                   }
               ]
           }
       )
       assert response.status_code == 200
       assert "content" in response.json()
   ```

2. **Test de Servicios**
   ```python
   # tests/test_ai_service.py
   async def test_process_chat():
       service = AIService()
       messages = [
           ChatMessage(role="user", content="¿Qué tablas hay?")
       ]
       response = await service.process_chat(messages)
       assert isinstance(response, ChatResponse)
       assert response.content
   ```

3. **Test de Base de Datos**
   ```python
   # tests/test_db.py
   def test_list_tables():
       with get_db_connection() as conn:
           with conn.cursor() as cur:
               cur.execute("""
                   SELECT table_name
                   FROM information_schema.tables
                   WHERE table_schema = 'public'
               """)
               tables = [row['table_name'] for row in cur.fetchall()]
               assert "usuarios" in tables
   ```

### Ejecutar Tests

1. **Todos los Tests**
   ```bash
   pytest
   ```

2. **Tests Específicos**
   ```bash
   pytest tests/test_chat.py
   ```

3. **Con Cobertura**
   ```bash
   pytest --cov=app tests/
   ```

## Mejores Prácticas

### 1. Código

- **Modularización**
  - Separar responsabilidades
  - Usar servicios
  - Mantener funciones pequeñas

- **Manejo de Errores**
  ```python
  try:
      result = await service.process_chat(messages)
  except ValueError as e:
      logger.error(f"Error en process_chat: {str(e)}")
      raise HTTPException(status_code=400, detail=str(e))
  ```

- **Logging**
  ```python
  import logging

  logger = logging.getLogger(__name__)

  def some_function():
      logger.info("Iniciando operación...")
      try:
          # ...
      except Exception as e:
          logger.error(f"Error: {str(e)}")
          raise
  ```

### 2. Base de Datos

- **Conexiones**
  ```python
  from contextlib import contextmanager

  @contextmanager
  def get_db_connection():
      conn = psycopg2.connect(db_connection_string)
      try:
          yield conn
      finally:
          conn.close()
  ```

- **Transacciones**
  ```python
  with get_db_connection() as conn:
      with conn.cursor() as cur:
          try:
              cur.execute("BEGIN")
              # ...
              cur.execute("COMMIT")
          except Exception as e:
              cur.execute("ROLLBACK")
              raise
  ```

### 3. Seguridad

- **Variables de Entorno**
  - Nunca exponer secretos
  - Usar `.env` para desarrollo
  - Usar secrets management en producción

- **Validación de Entradas**
  ```python
  from pydantic import BaseModel, EmailStr

  class UserCreate(BaseModel):
      nombre: str
      email: EmailStr
      password: str
  ```

- **Sanitización de SQL**
  ```python
  # Mal
  cur.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")

  # Bien
  cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
  ```

## Flujo de Trabajo

### 1. Desarrollo

1. **Crear Rama**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Desarrollar**
   - Escribir código
   - Escribir tests
   - Ejecutar tests
   - Documentar cambios

3. **Commit**
   ```bash
   git add .
   git commit -m "feat: agregar nueva funcionalidad"
   ```

### 2. Code Review

1. **Crear Pull Request**
   - Describir cambios
   - Referenciar issues
   - Solicitar review

2. **Review**
   - Revisar código
   - Ejecutar tests
   - Verificar documentación

3. **Merge**
   - Aprobar cambios
   - Merge a main
   - Eliminar rama

### 3. Despliegue

1. **Versión**
   ```bash
   # Actualizar versión
   bump2version patch
   ```

2. **Build**
   ```bash
   # Crear imagen Docker
   docker build -t api-rest-mcp .
   ```

3. **Deploy**
   ```bash
   # Desplegar
   docker-compose up -d
   ```

## Troubleshooting

### Problemas Comunes

1. **Error de Conexión a Base de Datos**
   ```python
   # Verificar URL
   print(f"DB URL: {os.getenv('SUPABASE_DB_URL')}")

   # Verificar conexión
   try:
       conn = psycopg2.connect(db_connection_string)
       print("Conexión exitosa")
   except Exception as e:
       print(f"Error de conexión: {str(e)}")
   ```

2. **Error de API Key**
   ```python
   # Verificar API key
   print(f"API Key length: {len(os.getenv('OPENAI_API_KEY'))}")

   # Probar API
   try:
       response = await openai.ChatCompletion.create(...)
       print("API funcionando")
   except Exception as e:
       print(f"Error de API: {str(e)}")
   ```

3. **Error de MCP**
   ```python
   # Verificar servidor MCP
   try:
       await mcp_server.start()
       print("Servidor MCP iniciado")
   except Exception as e:
       print(f"Error de MCP: {str(e)}")
   ```

### Logging y Depuración

1. **Configurar Logging**
   ```python
   import logging

   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('app.log'),
           logging.StreamHandler()
       ]
   )
   ```

2. **Usar Debugger**
   ```python
   import pdb

   def some_function():
       pdb.set_trace()
       # ...
   ```

3. **Profiling**
   ```python
   import cProfile

   profiler = cProfile.Profile()
   profiler.enable()
   # ...
   profiler.disable()
   profiler.print_stats()
   ``` 