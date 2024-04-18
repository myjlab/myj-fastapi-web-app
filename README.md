# Docker, FastAPI, MySQLを用いたTODOアプリのサンプル
## 前提条件
(WIP) dockerインストールのテキストを書く

## 起動方法
(WIP)　初回のみ

(WIP)　毎回必要

(WIP)　アクセス方法

## 開発の進め方
### api
(WIP) ディレクトリ構成の説明を含む

### DBのテーブル構造の変更について
- DBテーブルの定義はすべて`api/models`の**直下**に置く必要があります。(そうじゃないと読み込まれません)
- DBテーブルの構造を変更した場合、実際のDBに反映するためには以下のコマンドを実行する必要があります。
  - macの場合
  - `sh script/migrate_db.sh`
  - windowsの場合
  - (WIP)
- このコマンドは、DBのすべてのデータを削除します。今DBに存在するデータを`api/db_back_up`にバックアップされます。

### frontend
(WIP) ディレクトリ構成の説明を含む


# コマンド(コピペ用)
(WIP) 
- プロジェクトの起動
- テーブル構造の変更をDBに反映
- 新しいパッケージの追加

# 備考
(WIP)
TASA用prj説明


# FQA
(WIP) Windows one driveの説明

(WIP) 422 

(WIP) body: JSON.stringify(data),の時はheaders: {'Content-Type': 'application/json',}, 必須


# 以下、古いdocバックアップ
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

