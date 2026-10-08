# Yape Voz — Backend

Servidor Django de la app **Yape Voz Reporte**: usuarios, oyentes (quién puede escuchar
los pagos de quién) y aviso de pagos en tiempo real por WebSocket.

## Requisitos
- Python 3.11+
- PostgreSQL

## Instalación
```bash
pip install -r requirements.txt
cp .env.example .env        # completar DB_PASSWORD y DJANGO_SECRET_KEY
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Panel de administración: crear un usuario con `python manage.py createsuperuser`
y entrar a `/admin/`.

## API
Autenticación: header `Authorization: Token <token>`.

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/registro/` | `{username, password}` → `{token, username}` |
| POST | `/api/auth/login/` | `{username, password}` → `{token, username}` |
| GET | `/api/oyentes/` | Usuarios que pueden escuchar mis pagos |
| POST | `/api/oyentes/` | `{username, ver_historial}` agrega un oyente |
| PATCH | `/api/oyentes/<id>/` | `{ver_historial}` |
| DELETE | `/api/oyentes/<id>/` | Quita un oyente |
| GET | `/api/escucho/` | Usuarios cuyos pagos escucho |
| GET | `/api/escucho/<username>/pagos/` | Historial y total de hoy (si me dio permiso) |
| GET | `/api/pagos/` | Mis pagos y total de hoy |
| POST | `/api/pagos/` | `{id_local, remitente, monto, fecha}` registra un pago (no duplica por `id_local`) |

## Despliegue en Render
- **Build Command:** `./build.sh`
- **Start Command:** `daphne -b 0.0.0.0 -p $PORT yape_backend.asgi:application`
- **Variables de entorno:** `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`,
  `DJANGO_ALLOWED_HOSTS=.onrender.com`, `DJANGO_CSRF_TRUSTED_ORIGINS=https://<app>.onrender.com`,
  `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT=5432`, `DB_SSLMODE=require`

### WebSocket
`ws://<servidor>/ws/pagos/?token=<token>` — recibe
`{"tipo": "pago", "emisor", "id_local", "remitente", "monto", "fecha"}`
cada vez que un usuario que escucho recibe un Yape.

## Herramientas
`python tools/oyente_pc.py <usuario> <clave>` simula un celular oyente desde la PC
(muestra los pagos y los dice en voz alta con la voz de Windows).
