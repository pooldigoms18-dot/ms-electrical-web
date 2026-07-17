"""Configuración de Gunicorn para MS Electrical."""

# Gunicorn solamente será accesible desde el propio servidor.
# Nginx será el encargado de recibir las conexiones públicas.
bind = "127.0.0.1:8001"


# ============================================================
# Recursos
# ============================================================

# Configuración conservadora para un VPS pequeño.
workers = 1

worker_class = "gthread"

threads = 2


# ============================================================
# Tiempos
# ============================================================

timeout = 60

graceful_timeout = 30

keepalive = 5


# ============================================================
# Reciclado preventivo
# ============================================================

# Reiniciar periódicamente el worker ayuda a limitar
# crecimientos inesperados de memoria a largo plazo.
max_requests = 500

max_requests_jitter = 50


# ============================================================
# Logging
# ============================================================

accesslog = "-"

errorlog = "-"

loglevel = "info"

capture_output = True