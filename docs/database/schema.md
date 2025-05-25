# Esquema de la Base de Datos

## Introducción
Esta API utiliza una base de datos PostgreSQL alojada en Supabase. A continuación se detalla el esquema de la base de datos, las consultas comunes y las migraciones.

## Esquema

### Tabla: `usuarios`
Almacena la información de los usuarios registrados.

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Índices
- `usuarios_email_idx` (UNIQUE) ON `usuarios (email)`
- `usuarios_created_at_idx` ON `usuarios (created_at)`

### Tabla: `productos`
Almacena la información de los productos disponibles.

```sql
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripción TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Índices
- `productos_nombre_idx` ON `productos (nombre)`
- `productos_precio_idx` ON `productos (precio)`

### Tabla: `pedidos`
Registra los pedidos realizados por los usuarios.

```sql
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios (id) ON DELETE CASCADE,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'pendiente',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Índices
- `pedidos_usuario_id_idx` ON `pedidos (usuario_id)`
- `pedidos_estado_idx` ON `pedidos (estado)`

### Tabla: `detalles_pedido`
Almacena los detalles de cada pedido (líneas de pedido).

```sql
CREATE TABLE detalles_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER REFERENCES pedidos (id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos (id) ON DELETE CASCADE,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Índices
- `detalles_pedido_pedido_id_idx` ON `detalles_pedido (pedido_id)`
- `detalles_pedido_producto_id_idx` ON `detalles_pedido (producto_id)`

## Consultas Comunes

### 1. Obtener Usuario por Email
```sql
SELECT id, nombre, email, created_at
FROM usuarios
WHERE email = %s;
```

### 2. Listar Productos Disponibles
```sql
SELECT id, nombre, descripción, precio, stock
FROM productos
WHERE stock > 0
ORDER BY nombre;
```

### 3. Obtener Pedidos de un Usuario
```sql
SELECT p.id, p.total, p.estado, p.created_at,
       dp.cantidad, dp.precio_unitario, dp.subtotal,
       pr.nombre AS producto_nombre
FROM pedidos p
JOIN detalles_pedido dp ON p.id = dp.pedido_id
JOIN productos pr ON dp.producto_id = pr.id
WHERE p.usuario_id = %s
ORDER BY p.created_at DESC;
```

### 4. Actualizar Stock de Producto
```sql
UPDATE productos
SET stock = stock - %s,
    updated_at = CURRENT_TIMESTAMP
WHERE id = %s AND stock >= %s;
```

### 5. Insertar Nuevo Pedido
```sql
WITH nuevo_pedido AS (
    INSERT INTO pedidos (usuario_id, total, estado)
    VALUES (%s, %s, 'pendiente')
    RETURNING id
)
INSERT INTO detalles_pedido (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
SELECT np.id, %s, %s, p.precio, p.precio * %s
FROM nuevo_pedido np, productos p
WHERE p.id = %s;
```

## Migraciones

### Migración 1: Crear Tablas Iniciales
```sql
-- Crear tabla usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripción TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios (id) ON DELETE CASCADE,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'pendiente',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla detalles_pedido
CREATE TABLE detalles_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER REFERENCES pedidos (id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos (id) ON DELETE CASCADE,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Migración 2: Agregar Índices
```sql
-- Índices para usuarios
CREATE UNIQUE INDEX usuarios_email_idx ON usuarios (email);
CREATE INDEX usuarios_created_at_idx ON usuarios (created_at);

-- Índices para productos
CREATE INDEX productos_nombre_idx ON productos (nombre);
CREATE INDEX productos_precio_idx ON productos (precio);

-- Índices para pedidos
CREATE INDEX pedidos_usuario_id_idx ON pedidos (usuario_id);
CREATE INDEX pedidos_estado_idx ON pedidos (estado);

-- Índices para detalles_pedido
CREATE INDEX detalles_pedido_pedido_id_idx ON detalles_pedido (pedido_id);
CREATE INDEX detalles_pedido_producto_id_idx ON detalles_pedido (producto_id);
```

### Migración 3: Agregar Triggers
```sql
-- Trigger para actualizar updated_at en usuarios
CREATE OR REPLACE FUNCTION update_usuarios_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER usuarios_updated_at
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION update_usuarios_updated_at();

-- Trigger para actualizar updated_at en productos
CREATE OR REPLACE FUNCTION update_productos_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER productos_updated_at
    BEFORE UPDATE ON productos
    FOR EACH ROW
    EXECUTE FUNCTION update_productos_updated_at();

-- Trigger para actualizar updated_at en pedidos
CREATE OR REPLACE FUNCTION update_pedidos_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pedidos_updated_at
    BEFORE UPDATE ON pedidos
    FOR EACH ROW
    EXECUTE FUNCTION update_pedidos_updated_at();
```

## Mejores Prácticas

### 1. Índices
- Usar índices para columnas frecuentemente consultadas
- Evitar índices en columnas con baja cardinalidad
- Considerar índices parciales para consultas específicas

### 2. Constraints
- Usar `NOT NULL` para campos obligatorios
- Implementar `UNIQUE` para campos únicos
- Usar `FOREIGN KEY` para mantener integridad referencial

### 3. Tipos de Datos
- Usar `SERIAL` para IDs autoincrementales
- Usar `TIMESTAMP WITH TIME ZONE` para fechas
- Usar `DECIMAL` para valores monetarios

### 4. Seguridad
- Sanitizar todas las entradas
- Usar parámetros en consultas
- Limitar permisos de base de datos

### 5. Performance
- Optimizar consultas frecuentes
- Usar transacciones cuando sea necesario
- Mantener estadísticas actualizadas

## Troubleshooting

### Problemas Comunes

1. **Error de Conexión**
   ```python
   # Verificar la URL de conexión
   print(f"DB URL: {os.getenv('SUPABASE_DB_URL')}")
   ```

2. **Error de Permisos**
   ```python
   # Verificar permisos de la base de datos
   cur.execute("SELECT current_user, current_database()")
   ```

3. **Error de Timeout**
   ```python
   # Ajustar timeout de conexión
   conn = psycopg2.connect(
       db_connection_string,
       connect_timeout=10
   )
   ```

### Logging y Depuración
```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)
``` 