# myj-fastapi-web-app
A demo web app with FastAPI, vanilla JS


# For development
```bash
docker-compose up
sh script/migrate_db.sh
```
で動くはず

開発用スクりプトの説明
```bash
❯ tree script
script
├── add-package.sh  # sh script/add-package.sh <package_name>、コンテナ
├── migrate_db.sh　# sh script/migrate_db.sh、DBをマイグレーション
├── rebuild-api.sh　# sh script/rebuild-api.sh、APIコンテナを再ビルド
├── rebuild-frontend.sh　# sh script/rebuild-frontend.sh、フロントエンドコンテナを再ビルド
└── sata
    └── insert_mock.py　# python script/sata/insert_mock.py、モックデータをDBに挿入
    (ダメだったら、docker compose exec api poetry run python script/sata/insert_mock.py)

2 directories, 5 files
```

