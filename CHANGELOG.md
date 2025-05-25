# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-01

### Añadido
- Autenticación JWT
- Sistema de roles y permisos
- Rate limiting
- Logging estructurado
- Monitoreo de salud
- Documentación completa
- Ejemplos de uso
- Tests de integración
- CI/CD con GitHub Actions

### Cambiado
- Migrado a FastAPI 0.109.2
- Actualizado a Python 3.9+
- Mejorado sistema de logging
- Optimizado rendimiento de base de datos
- Refactorizado servicio MCP

### Eliminado
- Autenticación básica
- Endpoints obsoletos
- Código legacy
- Dependencias no utilizadas

### Corregido
- Memory leak en conexiones DB
- Race condition en MCP
- Errores de timezone
- Problemas de CORS
- Bugs de seguridad

## [1.1.0] - 2023-12-01

### Añadido
- Soporte para PostgreSQL 13
- Integración con OpenRouter
- Herramientas MCP adicionales
- Documentación de API
- Tests unitarios

### Cambiado
- Mejorado manejo de errores
- Optimizado queries SQL
- Actualizado dependencias
- Refactorizado modelos

### Corregido
- Errores de conexión DB
- Problemas de autenticación
- Bugs en endpoints
- Errores de validación

## [1.0.0] - 2023-11-01

### Añadido
- API REST básica
- Integración MCP inicial
- Autenticación básica
- Base de datos PostgreSQL
- Documentación básica
- Tests iniciales

### Cambiado
- Estructura del proyecto
- Configuración inicial
- Dependencias base

### Corregido
- Errores de configuración
- Problemas de instalación
- Bugs iniciales

## [0.2.0] - 2023-10-15

### Añadido
- Prototipo de API
- Integración MCP básica
- Estructura de proyecto
- README inicial

### Cambiado
- Diseño inicial
- Arquitectura base
- Dependencias

## [0.1.0] - 2023-10-01

### Añadido
- Proyecto inicial
- Estructura básica
- Dependencias mínimas
- Documentación inicial

## Notas de Versión

### 2.0.0
- Requiere Python 3.9+
- Requiere PostgreSQL 13+
- Cambios incompatibles en API
- Nueva autenticación JWT
- Mejoras de seguridad

### 1.1.0
- Compatible con Python 3.8+
- Compatible con PostgreSQL 12+
- Mejoras de rendimiento
- Nuevas funcionalidades

### 1.0.0
- Primera versión estable
- API básica funcional
- Integración MCP inicial
- Documentación completa

## Guía de Migración

### Migrando a 2.0.0
1. Actualizar Python a 3.9+
2. Actualizar PostgreSQL a 13+
3. Migrar a autenticación JWT
4. Actualizar clientes API
5. Revisar documentación

### Migrando a 1.1.0
1. Actualizar dependencias
2. Revisar cambios en API
3. Actualizar clientes
4. Verificar tests

### Migrando a 1.0.0
1. Instalar dependencias
2. Configurar base de datos
3. Revisar documentación
4. Ejecutar tests

## Contribuciones
Ver [CONTRIBUTING.md](docs/CONTRIBUTING.md) para detalles sobre cómo contribuir.

## Licencia
Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles. 