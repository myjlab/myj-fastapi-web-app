#!/bin/bash

docker-compose stop frontend
docker-compose rm frontend
docker rmi myj-fastapi-web-app-frontend
docker-compose build frontend --no-cache
