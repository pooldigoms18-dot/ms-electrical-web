#!/usr/bin/env bash

set -euo pipefail

APP_ROOT="/var/www/ms-electrical"

cd "$APP_ROOT"

echo "==> Descargando cambios..."
git pull --ff-only origin main

echo "==> Activando entorno virtual..."
source .venv/bin/activate

echo "==> Actualizando dependencias..."
python -m pip install \
    -r requirements-production.txt

echo "==> Aplicando migraciones..."
python manage.py migrate \
    --settings=config.settings_production

echo "==> Recopilando archivos estáticos..."
python manage.py collectstatic \
    --noinput \
    --settings=config.settings_production

echo "==> Comprobando Django..."
python manage.py check \
    --settings=config.settings_production

echo "==> Reiniciando aplicación..."
sudo systemctl restart ms-electrical

echo "==> Verificando servicio..."
sudo systemctl --no-pager \
    --full status ms-electrical

echo ""
echo "Actualización completada."