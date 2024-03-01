#!/bin/bash

# カレントディレクトリにdocker-compose.yamlがあるか確認
if [ ! -e docker-compose.yaml ]; then
    echo "docker-compose.yamlが見つかりません、docker-compose.yamlと同じディレクトリで実行してください"
    exit 1
fi

docker compose exec api poetry add "$@"
docker compose exec api poetry export --format requirements.txt --output requirements.txt
