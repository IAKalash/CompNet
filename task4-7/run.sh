#!/bin/bash

sudo docker rm -f pg-db my-parser-app 2>/dev/null
docker network create parser-net 2>/dev/null || true

docker run --name pg-db \
  --network parser-net \
  --env-file .env \
  -d postgres:15

sleep 5

docker build -t github-parser-app .
docker run --name my-parser-app \
  --network parser-net \
  --env-file .env \
  -p 8080:5000 \
  -d github-parser-app