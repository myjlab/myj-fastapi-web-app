@echo off

docker compose exec api poetry run python -m api.migrate_db
