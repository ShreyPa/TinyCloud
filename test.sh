#!/bin/bash

set -e

cd "$(dirname "$0")"

source .venv/bin/activate

set -a
source .env
set +a

export DB_HOST=localhost
export DB_USER=tinycloud
export DB_NAME=tinycloud_test
attempts=0
max_attempts=30

docker compose up -d db

until docker compose exec -T db pg_isready -U tinycloud
do
    attempts=$((attempts + 1))

    echo "Waiting for PostgreSQL... ($attempts/$max_attempts)"

    if [ "$attempts" -ge "$max_attempts" ]; then
        echo "PostgreSQL failed to start"
        exit 1
    fi

    sleep 1
done

echo "PostgreSQL is ready!"


cd api

python -m pytest -v