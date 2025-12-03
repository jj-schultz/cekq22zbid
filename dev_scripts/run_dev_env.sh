#!/usr/bin/env bash
set -euo pipefail
source .env

(cd "$BACKEND_DIR" && source .venv/bin/activate && python manage.py runserver $DJANGO_PORT) &
DJANGO_PID=$!

(cd $FRONTEND_DIR && npm run dev) &
VITE_PID=$!

trap 'kill $DJANGO_PID $VITE_PID' EXIT

wait