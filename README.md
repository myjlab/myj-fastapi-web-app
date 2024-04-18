# Docker, FastAPI, MySQLを用いたTODOアプリのサンプル
## 前提条件
(WIP) dockerインストールのテキストを書く

## 起動方法
1. 以下のコマンドを実行してprjのディレクトリに移動する
```bash 
cd
cd Desktop
cd myj-fastapi-web-app
```

2. 以下のコマンドを実行してprjを起動する
```bash
docker-compose up
```
※ ⚠️ ※ **注意** 初回はかなり時間がかかるので，下記のログが出力されるまではしばらく待機
<img width="800" alt="cmd.png" src="docs/images/docker-first-up-output.png">

3. **(初回のみ)** 以下のコマンドを実行してDBのテーブルを作成する

- macの場合
```bash
sh script/migrate_db.sh
```
   - windowsの場合
```bash
script\migrate_db.bat
```

### アクセス方法
すると、以下のURLでアクセスできます。
- API: http://localhost:8000/docs
- フロントエンド: http://localhost:3000

### 停止

docker-compose up コマンドを実行したウィンドウで `Ctrl + c`

## 開発の進め方
### api
(WIP) ディレクトリ構成の説明を含む

### DBのテーブル構造の変更について
- DBテーブルの定義はすべて`api/models`の**直下**に置く必要があります。(そうじゃないと読み込まれません)
- DBテーブルの構造を変更した場合、実際のDBに反映するためには以下のコマンドを実行する必要があります。
  - macの場合
  - `sh script/migrate_db.sh`
  - windowsの場合
  - `script\migrate_db.bat`
- このコマンドは、DBのすべてのデータを削除します。今DBに存在するデータを`api/db_back_up/`にバックアップされます。

### frontend
(WIP) ディレクトリ構成の説明を含む


## よく使うコマンドについて
コピペって使ってください

### プロジェクトの起動
1. `cd`
2. `cd Desktop`
3. `cd myj-fastapi-web-app`
4. `docker-compose up`

### テーブル構造の変更をDBに反映
macの場合: `sh script/migrate_db.sh`

windowsの場合: `script\migrate_db.bat`

### 新しいパッケージの追加
macの場合: `sh script/add-package.sh <パッケージ名>`

windowsの場合: `script\add-package.bat <パッケージ名>`

## FQA
## Q: Windowsにおいて、`cd Desktop`でエラーが出る
A: Windowsの場合、OneDriveの関係でDesktopが存在しない場合があります。その場合、`cd OneDrive`で移動して`dir`でディレクトリの一覧を確認しながら、`Desktop`か`デスクトップ`に移動してください。

## Q: フロントエンドでAPIを呼び出すと422エラーが出る
422は、リクエストの形式が正しくない場合に出るエラーです。以下の点を確認してください。

- API側で定義とた通りのリクエストを送っているか
  - `http://localhost:8000/docs` でAPIの仕様を確認できます。

- `fetch`の第2引数に`{ body: JSON.stringify(data) }`を指定している場合、`headers: { 'Content-Type': 'application/json' }` の指定が必要です。

## 備考
prj全体の構造は[`docs/prj-overview.md`](docs/prj-overview.md)を参照してください。

TASAとこのでもアプリ自体を開発する人は必ず読んでください。
