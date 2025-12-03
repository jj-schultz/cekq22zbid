#!/usr/bin/env bash
set -euo pipefail
source .env

# Find the highest python3.x available
PY_BIN=$(compgen -c python3. | grep -E '^python3\.[0-9]+$' | sort -V | tail -n1)

if [ -z "$PY_BIN" ]; then
  echo "ERROR: no python3.x found."
  exit 1
fi

PY_VERSION=$("$PY_BIN" -V 2>&1 | awk '{print $2}')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  echo "ERROR: latest python found is too old: $PY_VERSION"
  exit 1
fi

# other prereqs
command -v psql >/dev/null 2>&1 || { echo "ERROR: psql is not installed. install postgresql before continuing."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "ERROR: npm is not installed. install npm before continuing."; exit 1; }

(cd "$FRONTEND_DIR" && npm install)

cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
  "$PY_BIN" -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

# create database if it does not exist
if ! psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
  createdb "$DB_NAME"
fi

if ! (python manage.py migrate); then
  echo "ERROR: db migration failed"
  exit 1
fi

if ! (python manage.py test); then
  echo "ERROR: tests failed"
  exit 1
fi

if ! (python manage.py import_comments); then
  echo "ERROR: failed to import comments"
  exit 1
fi


cd "$PROJECT_ROOT"

echo
echo
echo
echo
echo
echo " █████╗ ██╗    ██╗███████╗███████╗  ██████╗ ███╗   ███╗███████╗"
echo "██╔══██╗██║    ██║██╔════╝██╔════╝╝██╔═══██╗████╗ ████║██╔════╝"
echo "███████║██║ █╗ ██║█████╗  ███████╗ ██║   ██║██╔████╔██║█████╗  "
echo "██╔══██║██║███╗██║██╔══╝  ╚════██║ ██║   ██║██║╚██╔╝██║██╔══╝  "
echo "██║  ██║╚███╔███╔╝███████╗███████║ ╚██████╔╝██║ ╚═╝ ██║███████╗"
echo "╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝  ╚════╝  ╚═╝     ╚═╝╚══════╝"
echo
echo "Dev env install successfull"
echo
echo "To run the dev server, execute"
echo "bash $PROJECT_ROOT/dev_scripts/run_dev_env.sh"
echo
echo "and then open http://localhost:$VITE_PORT in your favorite browser"
echo
