# Autenticación y Autorización

## Introducción
Este documento describe el sistema de autenticación y autorización implementado en la API REST con MCP. Utilizamos JWT (JSON Web Tokens) para la autenticación y un sistema de roles para la autorización.

## Flujo de Autenticación

### 1. Registro de Usuario
```http
POST /auth/register
Content-Type: application/json

{
    "nombre": "Usuario Ejemplo",
    "email": "usuario@ejemplo.com",
    "password": "contraseña_segura"
}
```

#### Response
```json
{
    "id": 1,
    "nombre": "Usuario Ejemplo",
    "email": "usuario@ejemplo.com",
    "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. Login
```http
POST /auth/login
Content-Type: application/json

{
    "email": "usuario@ejemplo.com",
    "password": "contraseña_segura"
}
```

#### Response
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### 3. Refresh Token
```http
POST /auth/refresh
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Implementación

### 1. Modelos de Datos
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: str
    user_id: int
    roles: list[str]
```

### 2. Middleware de Autenticación
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return await get_user(user_id)
    except JWTError:
        raise credentials_exception
```

### 3. Decoradores de Autorización
```python
from functools import wraps
from fastapi import HTTPException, status

def require_role(roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not any(role in current_user.roles for role in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos suficientes"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

## Roles y Permisos

### Roles Disponibles
1. **admin**
   - Acceso total a la API
   - Gestión de usuarios
   - Configuración del sistema

2. **user**
   - Acceso básico a la API
   - Gestión de su propio perfil
   - Operaciones CRUD básicas

3. **mcp_operator**
   - Acceso a operaciones MCP
   - Ejecución de consultas
   - Gestión de herramientas MCP

### Permisos por Endpoint

| Endpoint | Método | Roles Permitidos |
|----------|---------|-----------------|
| `/auth/*` | POST | Todos |
| `/users/*` | GET | admin, user |
| `/users/*` | POST | admin |
| `/users/*` | PUT | admin, user |
| `/users/*` | DELETE | admin |
| `/mcp/*` | POST | mcp_operator, admin |
| `/chat` | POST | user, admin, mcp_operator |

## Seguridad

### 1. Almacenamiento de Contraseñas
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 2. Configuración de JWT
```python
from datetime import datetime, timedelta
from typing import Optional

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
```

### 3. Rate Limiting
```python
from fastapi import Request
from fastapi.middleware.throttling import ThrottlingMiddleware

app.add_middleware(
    ThrottlingMiddleware,
    rate_limit=100,  # solicitudes por minuto
    time_window=60   # segundos
)
```

## Mejores Prácticas

### 1. Seguridad
- Usar HTTPS en producción
- Implementar rate limiting
- Rotar tokens regularmente
- Sanitizar todas las entradas
- Implementar bloqueo de cuenta
- Usar contraseñas fuertes

### 2. Tokens
- Tokens de acceso cortos (15-30 minutos)
- Tokens de refresh largos (7 días)
- Incluir claims mínimos necesarios
- Firmar con algoritmo fuerte (HS256)
- Rotar secretos regularmente

### 3. Contraseñas
- Mínimo 8 caracteres
- Requerir mayúsculas y minúsculas
- Requerir números
- Requerir caracteres especiales
- No permitir contraseñas comunes

## Ejemplos de Uso

### 1. Endpoint Protegido
```python
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/users")
@require_role(["admin"])
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user)
):
    return await create_new_user(user)
```

### 2. Cliente HTTP
```python
import httpx

async def get_protected_data():
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            "https://api.ejemplo.com/auth/login",
            json={
                "email": "usuario@ejemplo.com",
                "password": "contraseña_segura"
            }
        )
        token = response.json()["access_token"]

        # Usar token
        response = await client.get(
            "https://api.ejemplo.com/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## Troubleshooting

### 1. Problemas Comunes

#### Token Expirado
```json
{
    "detail": "Token expirado",
    "status_code": 401
}
```
Solución: Renovar el token usando el endpoint `/auth/refresh`

#### Credenciales Inválidas
```json
{
    "detail": "Credenciales inválidas",
    "status_code": 401
}
```
Solución: Verificar email y contraseña

#### Permisos Insuficientes
```json
{
    "detail": "No tiene permisos suficientes",
    "status_code": 403
}
```
Solución: Verificar roles del usuario

### 2. Depuración
```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar token
from jose import jwt
token_data = jwt.decode(
    token,
    settings.JWT_SECRET_KEY,
    algorithms=[settings.JWT_ALGORITHM]
)
print(token_data)
```

## Referencias
- [JWT.io](https://jwt.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) 