@echo off

:: カレントディレクトリにdocker-compose.yamlがあるか確認
if not exist docker-compose.yaml (
    echo docker-compose.yamlが見つかりません、docker-compose.yamlと同じディレクトリで実行してください
    exit /b 1
)


docker compose exec api poetry add %*
docker compose exec api poetry export --format requirements.txt --output requirements.txt
