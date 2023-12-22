#!/bin/bash

# カレントディレクトリにdocker-compose.yamlがあるか確認
if [ ! -e docker-compose.yaml ]; then
    echo "docker-compose.yamlが見つかりません、docker-compose.yamlと同じディレクトリで実行してください"
    exit 1
fi

sh script/in-container-poetry.sh add "$@"
# TODO: requirements.txtを更新する?
