#!/usr/bin/env bash
set -euo pipefail
source .env

(cd "$BACKEND_DIR" && source .venv/bin/activate && python manage.py test)