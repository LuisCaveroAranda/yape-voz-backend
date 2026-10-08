#!/usr/bin/env bash
# Build de Render: instala dependencias, prepara el CSS del /admin y crea/actualiza tablas.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
