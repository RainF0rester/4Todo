#!/usr/bin/bash

MODE=$(1:-dev)

mkdir -p ./data
if [ ! -f ./data/taskmaster.db ]; then
    touch ./data/taskmaster.db
    echo "Created taskmaster.db"
fi

docker compose down
if [ "$MODE" = "prod" ]; then
    # the command below is used for server in China mainland
    docker build -f Dockerfile.prod -t tasktracker:latest .
else
    docker build -t tasktracker:latest .
fi

docker compose up -d

echo "Done. Running at http://localhost:8080"
