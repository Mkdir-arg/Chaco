# Entorno Local

> Flujo recomendado de desarrollo local desde 2026-04-03.

## Comando principal

```bash
docker compose up --build
```

- URL principal: `http://localhost:8000/`
- Healthcheck: `http://localhost:8000/health/`
- Servicios incluidos: `app`, `mysql`, `redis`

## Qué hace el bootstrap automático

En cada arranque local, el contenedor `app` ejecuta solo:

1. Espera a que MySQL esté disponible
2. `python manage.py migrate --noinput`
3. `python manage.py crear_superadmin`
4. `python manage.py setup_grupos`
5. `python manage.py crear_programas`
6. Inicia `python manage.py runserver 0.0.0.0:8000` con autoreload

No ejecuta:

- `pip install -r requirements.txt`
- `sleep`
- `collectstatic`
- `load_initial_data`
- `setup_system`
- seeds demo pesados o frágiles

## Runtime local

- Default: `APP_RUNTIME=runserver`
- Alternativa: `APP_RUNTIME=daphne docker compose up --build`
- `runserver` se usa en local para tener autoreload sin volver a dividir el stack

## Credenciales y configuración

- Superadmin automático:
  - usuario: `admin`
  - contraseña: `mkdir123`
- Variables locales opcionales: copiar `.env.local.example` a `.env.local` y ajustar lo necesario
- Si no existe `.env.local`, Compose usa defaults seguros de desarrollo

## Reset del entorno

```bash
docker compose down -v
docker compose up --build
```

Esto borra los volúmenes locales de MySQL y Redis y reconstruye el entorno desde cero.

## Bootstrap opcional

Si necesitás ejecutar datos demo adicionales sin hacerlos obligatorios en cada restart:

```bash
LOCAL_OPTIONAL_BOOTSTRAP_COMMANDS="load_initial_data" docker compose up --build
```

Ese contrato deja el arranque diario liviano y mueve los seeds opcionales a una decisión explícita.
