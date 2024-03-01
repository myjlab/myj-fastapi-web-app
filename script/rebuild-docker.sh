#!/bin/bash

docker-compose stop api
docker-compose rm api
docker rmi myj-fastapi-web-app-api
docker-compose build --no-cache
