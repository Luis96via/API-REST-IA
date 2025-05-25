# Guía de Solución de Problemas

Esta guía proporciona soluciones para problemas comunes que pueden surgir durante el desarrollo, despliegue y uso de la API REST con MCP.

## Índice
1. [Problemas de Instalación](#problemas-de-instalación)
2. [Problemas de Configuración](#problemas-de-configuración)
3. [Problemas de Base de Datos](#problemas-de-base-de-datos)
4. [Problemas de API](#problemas-de-api)
5. [Problemas de MCP](#problemas-de-mcp)
6. [Problemas de Autenticación](#problemas-de-autenticación)
7. [Problemas de Rendimiento](#problemas-de-rendimiento)
8. [Problemas de Despliegue](#problemas-de-despliegue)
9. [Problemas de Seguridad](#problemas-de-seguridad)
10. [Recursos Adicionales](#recursos-adicionales)

## Problemas de Instalación

### Error: No se pueden instalar las dependencias
```bash
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solución:**
1. Usar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. Instalar con permisos de usuario:
```bash
pip install --user -r requirements.txt
```

### Error: Versión de Python incompatible
```bash
ERROR: Package 'fastapi' requires Python '>=3.9' but the running Python is 3.8.0
```

**Solución:**
1. Actualizar Python:
```bash
# Windows
winget install Python.Python.3.9

# Linux
sudo apt update
sudo apt install python3.9
```

2. Verificar versión:
```bash
python --version
```

## Problemas de Configuración

### Error: Variables de entorno no encontradas
```python
KeyError: 'DATABASE_URL'
```

**Solución:**
1. Verificar archivo `.env`:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
MCP_API_KEY=your_api_key
```

2. Cargar variables manualmente:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Error: Configuración de base de datos incorrecta
```python
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solución:**
1. Verificar conexión:
```bash
psql -h localhost -U user -d dbname
```

2. Revisar configuración:
```python
DATABASE_URL="postgresql://user:pass@localhost:5432/dbname?sslmode=disable"
```

## Problemas de Base de Datos

### Error: Migraciones fallidas
```bash
alembic.exc.CommandError: Can't locate revision identified by '123abc'
```

**Solución:**
1. Reiniciar migraciones:
```bash
# Eliminar base de datos
dropdb dbname

# Crear nueva base de datos
createdb dbname

# Ejecutar migraciones
alembic upgrade head
```

2. Verificar historial:
```bash
alembic history
```

### Error: Conexiones agotadas
```python
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached
```

**Solución:**
1. Ajustar pool de conexiones:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30
)
```

2. Cerrar conexiones explícitamente:
```python
async with AsyncSession(engine) as session:
    # operaciones
    await session.close()
```

## Problemas de API

### Error: Endpoint no encontrado
```python
fastapi.exceptions.HTTPException: 404 Not Found
```

**Solución:**
1. Verificar ruta:
```python
@app.get("/api/v1/endpoint")  # Asegurar que la ruta es correcta
```

2. Revisar documentación:
```bash
curl http://localhost:8000/docs
```

### Error: Validación de datos
```python
pydantic.error_wrappers.ValidationError: 1 validation error for User
```

**Solución:**
1. Revisar modelo:
```python
class User(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)
```

2. Validar datos:
```python
try:
    user = User(**data)
except ValidationError as e:
    print(e.json())
```

## Problemas de MCP

### Error: Timeout en MCP
```python
MCPTimeoutError: Request timed out after 30 seconds
```

**Solución:**
1. Ajustar timeout:
```python
mcp_client = MCPClient(timeout=60)
```

2. Implementar retry:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def mcp_request():
    return await mcp_client.chat(message)
```

### Error: Respuesta inválida de MCP
```python
MCPError: Invalid response format
```

**Solución:**
1. Verificar formato:
```python
response = await mcp_client.chat(message)
if not isinstance(response, dict):
    raise MCPError("Invalid response format")
```

2. Implementar fallback:
```python
try:
    response = await mcp_client.chat(message)
except MCPError:
    response = await fallback_chat(message)
```

## Problemas de Autenticación

### Error: Token expirado
```python
jwt.exceptions.ExpiredSignatureError: Signature has expired
```

**Solución:**
1. Refrescar token:
```python
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        return create_access_token(payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

2. Ajustar tiempo de expiración:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### Error: Permisos insuficientes
```python
fastapi.exceptions.HTTPException: 403 Forbidden
```

**Solución:**
1. Verificar roles:
```python
@router.get("/admin")
async def admin_endpoint(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
```

2. Actualizar permisos:
```sql
UPDATE users SET role = 'admin' WHERE username = 'user';
```

## Problemas de Rendimiento

### Error: Alta latencia
```python
TimeoutError: Request took too long to complete
```

**Solución:**
1. Optimizar consultas:
```python
# Antes
users = await db.query(User).all()

# Después
users = await db.query(User).options(selectinload(User.profile)).all()
```

2. Implementar caché:
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@router.get("/cached")
@cache(expire=300)
async def cached_endpoint():
    return await expensive_operation()
```

### Error: Alto uso de memoria
```python
MemoryError: Unable to allocate memory
```

**Solución:**
1. Optimizar uso de memoria:
```python
# Usar generadores
async def stream_large_data():
    async for chunk in db.stream_query():
        yield chunk
```

2. Ajustar límites:
```python
# Configurar límites de memoria
import resource
resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, -1))
```

## Problemas de Despliegue

### Error: Servicio no inicia
```bash
systemd[1]: api.service: Failed to start
```

**Solución:**
1. Verificar logs:
```bash
journalctl -u api.service -n 50
```

2. Revisar configuración:
```ini
[Unit]
Description=API REST Service
After=network.target

[Service]
User=api
WorkingDirectory=/opt/api
Environment=PYTHONPATH=/opt/api
ExecStart=/opt/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Error: Nginx no enruta
```nginx
502 Bad Gateway
```

**Solución:**
1. Verificar configuración Nginx:
```nginx
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

2. Revisar logs:
```bash
tail -f /var/log/nginx/error.log
```

## Problemas de Seguridad

### Error: Ataque de fuerza bruta
```python
TooManyRequests: Rate limit exceeded
```

**Solución:**
1. Implementar rate limiting:
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.get("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def limited_endpoint():
    return {"message": "Hello"}
```

2. Configurar firewall:
```bash
# Bloquear IPs maliciosas
iptables -A INPUT -p tcp --dport 8000 -m state --state NEW -m recent --set
iptables -A INPUT -p tcp --dport 8000 -m state --state NEW -m recent --update --seconds 60 --hitcount 10 -j DROP
```

### Error: Vulnerabilidades de seguridad
```bash
safety check
Found 3 known security vulnerabilities
```

**Solución:**
1. Actualizar dependencias:
```bash
pip install --upgrade -r requirements.txt
```

2. Escanear código:
```bash
bandit -r .
safety check
```

## Recursos Adicionales

### Documentación
- [FastAPI Troubleshooting](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [PostgreSQL Troubleshooting](https://www.postgresql.org/docs/current/static/runtime-config.html)
- [Nginx Troubleshooting](https://nginx.org/en/docs/beginners_guide.html)

### Herramientas
- [pgAdmin](https://www.pgadmin.org/) - Administración de PostgreSQL
- [Postman](https://www.postman.com/) - Pruebas de API
- [Grafana](https://grafana.com/) - Monitoreo
- [Sentry](https://sentry.io/) - Tracking de errores

### Contacto
Para soporte técnico:
- Email: support@ejemplo.com
- Slack: #support-team
- Teléfono: +1-234-567-8900 