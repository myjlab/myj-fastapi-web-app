#!/bin/bash

docker-compose stop demo-app
docker-compose rm demo-app
docker rmi myj-fastapi-web-app-backend
docker-compose build --no-cache
