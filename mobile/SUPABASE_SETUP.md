# Configuración de Supabase para la App Móvil

## Pasos para conectar tu app a Supabase

### 1. Crea un proyecto en Supabase
1. Ve a [supabase.com](https://supabase.com)
2. Haz login o crea una cuenta
3. Crea un nuevo proyecto
4. Guarda las credenciales (URL y ANON_KEY)

### 2. Copia tus credenciales
En el archivo `.env` de tu carpeta `mobile/`, reemplaza:
```
EXPO_PUBLIC_SUPABASE_URL=https://tu-proyecto.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=tu-anon-key-aqui
```

Con tus credenciales reales que obtendrás de:
- Project Settings → API → Project URL
- Project Settings → API → anon (public) Key

### 3. Crea las tablas en Supabase
Ve a SQL Editor en tu panel de Supabase y ejecuta estas queries:

```sql
-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  foto VARCHAR(500),
  es_admin BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  activo BOOLEAN DEFAULT true
);

-- Tabla de Grupos
CREATE TABLE IF NOT EXISTS grupos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL UNIQUE,
  descripcion VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de relación Usuario-Grupo (muchos a muchos)
CREATE TABLE IF NOT EXISTS usuario_grupos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  grupo_id UUID NOT NULL REFERENCES grupos(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(usuario_id, grupo_id)
);

-- Crear índices
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuario_grupos_usuario_id ON usuario_grupos(usuario_id);
CREATE INDEX idx_usuario_grupos_grupo_id ON usuario_grupos(grupo_id);

-- Habilitar Row Level Security (RLS)
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE grupos ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuario_grupos ENABLE ROW LEVEL SECURITY;
```

### 4. Inserta datos de prueba (opcional)
```sql
-- Crear grupos
INSERT INTO grupos (nombre, descripcion) VALUES 
('Administradores', 'Acceso total al sistema'),
('Usuarios', 'Usuarios normales'),
('Moderadores', 'Moderadores del sistema');

-- Crear usuario de prueba
-- Nota: Las contraseñas están en TEXTO PLANO por ahora. Para producción, usa bcrypt
INSERT INTO usuarios (username, password, nombre, es_admin) VALUES 
('admin', 'admin123', 'Administrador', true),
('usuario', 'usuario123', 'Usuario Demo', false);

-- Asignar grupos a usuarios
INSERT INTO usuario_grupos (usuario_id, grupo_id) 
SELECT u.id, g.id FROM usuarios u, grupos g 
WHERE u.username = 'admin' AND g.nombre = 'Administradores';

INSERT INTO usuario_grupos (usuario_id, grupo_id) 
SELECT u.id, g.id FROM usuarios u, grupos g 
WHERE u.username = 'usuario' AND g.nombre = 'Usuarios';
```

### 5. Prueba el login
- Inicia la app: `npm start`
- Usa las credenciales:
  - Usuario: `admin`
  - Contraseña: `admin123`

## Problemas comunes

**Error de conexión a Supabase:**
- Asegúrate de que el archivo `.env` tiene las credenciales correctas
- Reinicia la app después de cambiar el `.env`

**Usuario no encontrado:**
- Verifica que el usuario esté en la tabla `usuarios`
- Comprueba que la columna `activo` sea `true`

**Contraseña incorrecta:**
- Asegúrate de escribir la contraseña exactamente como en la BD
- En producción, te recomendamos usar bcrypt para hashear contraseñas

## Próximos pasos

- [ ] Implementar validación de contraseñas en el backend
- [ ] Agregar cifrado de contraseñas con bcrypt
- [ ] Configurar Row Level Security (RLS) policies
- [ ] Agregar pantalla de registro
- [ ] Implementar recuperación de contraseña
