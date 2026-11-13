#!/bin/bash
set -e

cd "$(dirname "$0")"

source .venv/bin/activate

set -a
source .env
set +a

export DB_HOST=localhost

docker compose up -d db

cd api
python main.py