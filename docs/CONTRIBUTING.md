# Guía de Contribución

## Introducción
¡Gracias por tu interés en contribuir a API REST con MCP! Este documento proporciona las directrices y el proceso para contribuir al proyecto.

## Código de Conducta

### Nuestros Compromisos
- Mantener un ambiente acogedor y respetuoso
- Aceptar críticas constructivas
- Enfocarnos en lo mejor para la comunidad
- Mostrar empatía hacia otros miembros

### Nuestras Responsabilidades
- Establecer criterios claros de comportamiento
- Tomar acciones correctivas justas
- Aceptar responsabilidad por nuestras acciones
- Aprender de los errores

## Cómo Contribuir

### 1. Reportar Bugs
- Usar el issue tracker de GitHub
- Usar la plantilla de bug report
- Incluir pasos para reproducir
- Describir el comportamiento esperado
- Incluir capturas de pantalla si es relevante
- Especificar versión y entorno

### 2. Sugerir Mejoras
- Usar el issue tracker de GitHub
- Usar la plantilla de feature request
- Describir el problema que resuelve
- Proponer una solución
- Considerar alternativas
- Incluir ejemplos de uso

### 3. Pull Requests
- Crear una rama descriptiva
- Seguir las convenciones de código
- Incluir tests
- Actualizar documentación
- Describir cambios
- Referenciar issues

## Proceso de Desarrollo

### 1. Configuración del Entorno
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/api-rest-mcp.git
cd api-rest-mcp

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Convenciones de Código

#### Python
- Seguir PEP 8
- Usar type hints
- Documentar funciones y clases
- Mantener líneas < 88 caracteres
- Usar black para formateo
- Usar isort para imports

#### SQL
- Usar mayúsculas para palabras clave
- Indentar consultas complejas
- Comentar secciones importantes
- Usar nombres descriptivos
- Seguir convenciones de nomenclatura

### 3. Testing
```bash
# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=app tests/

# Ejecutar linting
flake8
black --check .
isort --check-only .
mypy .
```

### 4. Documentación
- Actualizar README.md
- Documentar nuevos endpoints
- Actualizar ejemplos
- Mantener docstrings
- Seguir estilo Google

## Flujo de Trabajo

### 1. Crear Rama
```bash
# Crear rama desde main
git checkout main
git pull origin main
git checkout -b feature/nueva-funcionalidad
```

### 2. Desarrollar
- Escribir código
- Escribir tests
- Ejecutar tests
- Formatear código
- Actualizar documentación

### 3. Commit
```bash
# Verificar cambios
git status
git diff

# Agregar cambios
git add .

# Crear commit
git commit -m "feat: agregar nueva funcionalidad

- Descripción detallada
- Referencia a issue #123"
```

### 4. Push
```bash
# Subir cambios
git push origin feature/nueva-funcionalidad
```

### 5. Pull Request
- Crear PR en GitHub
- Describir cambios
- Referenciar issues
- Solicitar review
- Esperar aprobación

## Convenciones de Commits

### Formato
```
tipo(alcance): descripción

[cuerpo opcional]

[pie opcional]
```

### Tipos
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación
- `style`: Formato
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Mantenimiento

### Ejemplos
```
feat(auth): agregar autenticación JWT

- Implementar login
- Agregar refresh token
- Documentar endpoints

Closes #123
```

## Code Review

### Criterios
- Código limpio y legible
- Tests completos
- Documentación actualizada
- Sin regresiones
- Cumple convenciones

### Proceso
1. Revisar cambios
2. Probar funcionalidad
3. Verificar tests
4. Comentar sugerencias
5. Aprobar o solicitar cambios

## Versiones

### Semántica
- MAJOR: Cambios incompatibles
- MINOR: Nueva funcionalidad compatible
- PATCH: Correcciones compatibles

### Ejemplo
```bash
# Actualizar versión
bump2version patch  # 1.0.0 -> 1.0.1
bump2version minor  # 1.0.1 -> 1.1.0
bump2version major  # 1.1.0 -> 2.0.0
```

## Recursos

### Documentación
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [MCP](https://mcp-docs.ejemplo.com/)

### Herramientas
- [Black](https://black.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)
- [flake8](https://flake8.pycqa.org/)
- [mypy](https://mypy.readthedocs.io/)
- [pytest](https://docs.pytest.org/)

## Contacto

### Mantenedores
- Nombre: [Tu Nombre]
- Email: tu@email.com
- GitHub: @tu-usuario

### Canales
- Issues: GitHub Issues
- Chat: Discord/Slack
- Email: soporte@ejemplo.com

## Licencia
Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles. 