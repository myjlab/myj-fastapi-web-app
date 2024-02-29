#!/bin/bash

# カレントディレクトリにdocker-compose.yamlがあるか確認
if [ ! -e docker-compose.yaml ]; then
    echo "docker-compose.yamlが見つかりません、docker-compose.yamlと同じディレクトリで実行してください"
    exit 1
fi

docker compose exec demo-app poetry add "$@"
# TODO: requirements.txtを更新する?
# TODO: localのpoetry環境を更新する?
