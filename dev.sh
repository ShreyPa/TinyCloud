#!/bin/bash
set -e

cd "$(dirname "$0")"

source .venv/bin/activate

set -a
source .env
set +a

export FLASK_HOST=127.0.0.1
export FLASK_PORT=5001
export FLASK_DEBUG=true

export DB_HOST=localhost

docker compose up -d db

cd api
python main.py