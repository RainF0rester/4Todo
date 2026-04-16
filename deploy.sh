#!/usr/bin/bash

mkdir -p ./data
if [ ! -f ./data/taskmaster.db ]; then
    touch ./data/taskmaster.db
    echo "Created taskmaster.db"
fi

docker compose down
docker build -f Dockerfile.prod -t tasktracker:latest .
docker compose up -d

echo "Done. Running at http://localhost:8080"
