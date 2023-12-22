#!/bin/bash

docker compose run --rm --entrypoint "poetry install --no-root" demo-app
