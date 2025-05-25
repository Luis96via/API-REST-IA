# Guía de Despliegue

## Requisitos del Sistema

### Requisitos Mínimos
- CPU: 2 cores
- RAM: 4GB
- Almacenamiento: 20GB SSD
- Sistema Operativo: Ubuntu 20.04 LTS o superior

### Requisitos Recomendados
- CPU: 4 cores
- RAM: 8GB
- Almacenamiento: 40GB SSD
- Sistema Operativo: Ubuntu 22.04 LTS

### Dependencias del Sistema
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y \
    python3.9 \
    python3.9-venv \
    postgresql-13 \
    nginx \
    supervisor \
    certbot \
    python3-certbot-nginx
```

## Preparación del Entorno

### 1. Configuración de Python
```bash
# Crear directorio de la aplicación
sudo mkdir -p /opt/api-rest-mcp
sudo chown $USER:$USER /opt/api-rest-mcp

# Crear entorno virtual
python3.9 -m venv /opt/api-rest-mcp/venv
source /opt/api-rest-mcp/venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de PostgreSQL
```bash
# Crear base de datos
sudo -u postgres psql -c "CREATE DATABASE api_rest_mcp;"
sudo -u postgres psql -c "CREATE USER api_user WITH PASSWORD 'tu_contraseña_segura';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE api_rest_mcp TO api_user;"

# Aplicar migraciones
psql -U api_user -d api_rest_mcp -f migrations/001_initial.sql
```

### 3. Configuración de Variables de Entorno
```bash
# Crear archivo .env
cat > /opt/api-rest-mcp/.env << EOL
# OpenRouter
OPENAI_API_KEY=sk-or-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=openai/gpt-3.5-turbo-1106
SITE_URL=https://tu-dominio.com
SITE_NAME=API-REST-MCP

# Base de Datos
SUPABASE_DB_URL=postgresql://api_user:tu_contraseña_segura@localhost:5432/api_rest_mcp

# MCP
MCP_HOST=localhost
MCP_PORT=3000

# Seguridad
JWT_SECRET_KEY=tu_clave_secreta_muy_segura
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOL

# Asegurar permisos
chmod 600 /opt/api-rest-mcp/.env
```

## Configuración de Nginx

### 1. Instalar Certificado SSL
```bash
# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com
```

### 2. Configurar Nginx
```nginx
# /etc/nginx/sites-available/api-rest-mcp
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /mcp {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 3. Activar Configuración
```bash
sudo ln -s /etc/nginx/sites-available/api-rest-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Configuración de Supervisor

### 1. Configurar Supervisor
```ini
# /etc/supervisor/conf.d/api-rest-mcp.conf
[program:api-rest-mcp]
directory=/opt/api-rest-mcp
command=/opt/api-rest-mcp/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/api-rest-mcp/err.log
stdout_logfile=/var/log/api-rest-mcp/out.log
environment=
    PATH="/opt/api-rest-mcp/venv/bin:%(ENV_PATH)s",
    PYTHONPATH="/opt/api-rest-mcp"

[program:mcp-server]
directory=/opt/api-rest-mcp
command=/opt/api-rest-mcp/venv/bin/python -m app.services.mcp_service
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/api-rest-mcp/mcp-err.log
stdout_logfile=/var/log/api-rest-mcp/mcp-out.log
```

### 2. Activar Supervisor
```bash
sudo mkdir -p /var/log/api-rest-mcp
sudo chown www-data:www-data /var/log/api-rest-mcp
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

## Monitoreo

### 1. Health Checks
```bash
# Verificar estado de la API
curl https://tu-dominio.com/health

# Verificar logs
sudo tail -f /var/log/api-rest-mcp/out.log
sudo tail -f /var/log/api-rest-mcp/err.log
```

### 2. Métricas
- Implementar Prometheus para métricas
- Configurar Grafana para visualización
- Monitorear:
  - Uso de CPU/RAM
  - Latencia de API
  - Errores
  - Uso de base de datos

### 3. Alertas
- Configurar alertas en Grafana
- Monitorear:
  - Errores HTTP 5xx
  - Latencia alta
  - Uso de recursos
  - Errores de base de datos

## Mantenimiento

### 1. Actualizaciones
```bash
# Actualizar código
cd /opt/api-rest-mcp
git pull origin main

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Aplicar migraciones
psql -U api_user -d api_rest_mcp -f migrations/latest.sql

# Reiniciar servicios
sudo supervisorctl restart all
```

### 2. Backups
```bash
# Backup de base de datos
pg_dump -U api_user api_rest_mcp > backup_$(date +%Y%m%d).sql

# Backup de archivos
tar -czf api-rest-mcp_$(date +%Y%m%d).tar.gz /opt/api-rest-mcp
```

### 3. Logs
```bash
# Rotación de logs
sudo logrotate -f /etc/logrotate.d/api-rest-mcp

# Limpieza de logs antiguos
find /var/log/api-rest-mcp -name "*.log" -mtime +30 -delete
```

## Seguridad

### 1. Firewall
```bash
# Configurar UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Actualizaciones de Seguridad
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Actualizar dependencias Python
pip install --upgrade -r requirements.txt
```

### 3. Auditoría
- Revisar logs regularmente
- Monitorear intentos de acceso
- Realizar escaneos de seguridad
- Mantener certificados SSL actualizados

## Troubleshooting

### 1. Problemas Comunes

#### API no responde
```bash
# Verificar logs
sudo tail -f /var/log/api-rest-mcp/err.log

# Verificar estado del servicio
sudo supervisorctl status api-rest-mcp
```

#### Errores de Base de Datos
```bash
# Verificar conexión
psql -U api_user -d api_rest_mcp -c "SELECT 1;"

# Verificar logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### Problemas de SSL
```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificado
sudo certbot renew --dry-run
```

### 2. Recuperación

#### Restaurar Base de Datos
```bash
# Restaurar desde backup
psql -U api_user -d api_rest_mcp < backup_20240101.sql
```

#### Recuperar Servicio
```bash
# Reiniciar todos los servicios
sudo supervisorctl restart all
sudo systemctl restart nginx
```

## Escalabilidad

### 1. Horizontal
- Usar balanceador de carga
- Configurar múltiples instancias
- Implementar caché distribuido

### 2. Vertical
- Aumentar recursos del servidor
- Optimizar configuración de PostgreSQL
- Ajustar workers de uvicorn

## Contacto y Soporte

### 1. Soporte Técnico
- Email: soporte@tu-dominio.com
- Teléfono: +XX XXX XXX XXX
- Horario: Lunes a Viernes 9:00-18:00

### 2. Documentación Adicional
- [Documentación de API](./api/endpoints.md)
- [Guía de Desarrollo](./DEVELOPMENT.md)
- [Configuración](./CONFIGURATION.md) 