# Guía de Pruebas

Esta guía detalla las estrategias y procedimientos de prueba para la API REST con MCP.

## Índice
1. [Estrategia de Pruebas](#estrategia-de-pruebas)
2. [Tipos de Pruebas](#tipos-de-pruebas)
3. [Configuración del Entorno](#configuración-del-entorno)
4. [Ejecución de Pruebas](#ejecución-de-pruebas)
5. [Cobertura de Código](#cobertura-de-código)
6. [Pruebas de Integración](#pruebas-de-integración)
7. [Pruebas de Rendimiento](#pruebas-de-rendimiento)
8. [Pruebas de Seguridad](#pruebas-de-seguridad)
9. [Mantenimiento de Pruebas](#mantenimiento-de-pruebas)

## Estrategia de Pruebas

### Objetivos
- Asegurar la calidad del código
- Mantener la estabilidad de la API
- Prevenir regresiones
- Validar la integración con MCP
- Garantizar la seguridad

### Enfoque
- Pruebas automatizadas
- Integración continua
- Revisión de código
- Monitoreo continuo

## Tipos de Pruebas

### Pruebas Unitarias
```python
# Ejemplo de prueba unitaria
def test_user_creation():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepass123"
    }
    user = create_user(user_data)
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
    assert user.is_active == True
```

### Pruebas de Integración
```python
# Ejemplo de prueba de integración
async def test_mcp_chat_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        response = await client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Chat con MCP
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/mcp/chat",
            json={"message": "Hola MCP"},
            headers=headers
        )
        assert response.status_code == 200
        assert "response" in response.json()
```

### Pruebas de API
```python
# Ejemplo de prueba de API
def test_api_endpoints():
    with TestClient(app) as client:
        # Probar endpoint público
        response = client.get("/health")
        assert response.status_code == 200
        
        # Probar endpoint protegido
        response = client.get("/api/protected")
        assert response.status_code == 401
        
        # Probar con token válido
        token = get_test_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/protected", headers=headers)
        assert response.status_code == 200
```

## Configuración del Entorno

### Requisitos
- Python 3.9+
- pytest
- pytest-asyncio
- pytest-cov
- httpx
- aiohttp
- locust (para pruebas de carga)

### Instalación
```bash
# Instalar dependencias de prueba
pip install -r requirements-test.txt

# Configurar base de datos de prueba
pytest --setup-db
```

### Variables de Entorno
```env
TESTING=true
TEST_DATABASE_URL=postgresql://test:test@localhost:5432/test_db
TEST_MCP_API_KEY=test_key
```

## Ejecución de Pruebas

### Comandos Básicos
```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas específicas
pytest tests/test_auth.py
pytest tests/test_mcp.py

# Ejecutar con cobertura
pytest --cov=app tests/

# Ejecutar pruebas de rendimiento
locust -f tests/load/locustfile.py
```

### Opciones de pytest
```bash
# Ejecutar en modo verbose
pytest -v

# Mostrar prints
pytest -s

# Ejecutar pruebas fallidas
pytest --lf

# Ejecutar pruebas marcadas
pytest -m "integration"
```

## Cobertura de Código

### Configuración
```ini
# .coveragerc
[run]
source = app
omit = 
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

### Generación de Reportes
```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Generar reporte XML
pytest --cov=app --cov-report=xml
```

## Pruebas de Integración

### Base de Datos
```python
# Fixture de base de datos
@pytest.fixture
async def db():
    async with AsyncDatabase() as db:
        await db.create_all()
        yield db
        await db.drop_all()
```

### MCP
```python
# Fixture de MCP
@pytest.fixture
async def mcp_client():
    async with MCPClient() as client:
        yield client
```

## Pruebas de Rendimiento

### Carga
```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def test_chat(self):
        self.client.post("/mcp/chat", json={
            "message": "Test message"
        })
```

### Estrés
```python
# test_stress.py
async def test_concurrent_requests():
    async with AsyncClient() as client:
        tasks = [
            client.post("/mcp/chat", json={"message": f"Test {i}"})
            for i in range(100)
        ]
        responses = await asyncio.gather(*tasks)
        assert all(r.status_code == 200 for r in responses)
```

## Pruebas de Seguridad

### Autenticación
```python
def test_jwt_security():
    # Probar token expirado
    expired_token = create_expired_token()
    response = client.get("/api/protected", 
                         headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    
    # Probar token inválido
    invalid_token = "invalid.token.here"
    response = client.get("/api/protected",
                         headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401
```

### Autorización
```python
def test_role_permissions():
    # Probar acceso admin
    admin_token = create_admin_token()
    response = client.get("/api/admin",
                         headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    
    # Probar acceso usuario normal
    user_token = create_user_token()
    response = client.get("/api/admin",
                         headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
```

## Mantenimiento de Pruebas

### Buenas Prácticas
1. Mantener pruebas independientes
2. Usar fixtures apropiadamente
3. Limpiar datos de prueba
4. Documentar casos de prueba
5. Mantener actualizadas las pruebas

### Actualización de Pruebas
1. Revisar pruebas al cambiar código
2. Actualizar fixtures cuando sea necesario
3. Mantener documentación actualizada
4. Revisar cobertura periódicamente

## Recursos

### Documentación
- [pytest](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Locust](https://docs.locust.io/)

### Herramientas
- pytest
- pytest-cov
- locust
- aiohttp
- httpx

### Contacto
Para preguntas sobre pruebas, contactar al equipo de QA:
- Email: qa@ejemplo.com
- Slack: #qa-team 