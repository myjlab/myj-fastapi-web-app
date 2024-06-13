# Docker, FastAPI, MySQLを用いたTODOアプリのサンプル
## 前提条件
Dockerのインストールを完了させておくこと

- [Windows10の場合](docs/install-docker-windows10.md)
- [Windows11の場合](docs/install-docker-windows11.md)
- [Macの場合](docs/install-docker-mac.md)


## 起動方法
1. 以下のコマンドを実行してprjのディレクトリに移動します。
```bash 
cd
cd Desktop
cd myj-fastapi-web-app-main
```

2. 以下のコマンドを実行してprjを起動します。
```bash
docker-compose up
```
※ ⚠️ ※ **注意** 初回はかなり時間がかかるので，下記のログが出力されるまではしばらく待機
<img width="800" alt="cmd.png" src="docs/images/docker-first-up-output.png">

3. **(初回のみ)** 以下のコマンドを実行してDBのテーブルを作成します。

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

### DBの内部を直接確認したい、操作したい
こちらのドキュメント[how-to-use-vscode-mysql-plugin.md](docs/how-to-use-vscode-mysql-plugin.md)を参照してください。

### 停止

docker-compose up コマンドを実行したウィンドウで `Ctrl + c`。

## 開発の進め方
### api
基本的には`api`ディレクトリのファイルを編集して開発を進めていきます。
- `api`ディレクトリの構成は以下の通りです。
  - `api`
    - `models/*`: DBのテーブル構造を定義するファイルを置きます。
    - `routers/*`: APIのエンドポイントを定義するファイルを置きます。
    - `schemas/*`: APIのリクエストとレスポンスの受け渡しデータの構造を定義するファイルを置きます。
    - `cruds/*`: DBの操作を行うファイルを置きます。
    - `db.py`: DBの接続情報を定義するファイルを置きます。

### DBのテーブル構造の変更について
- DBテーブルの定義はすべて`api/models`の**直下**に置く必要があります。(そうじゃないと読み込まれません)
- DBテーブルの構造を変更した場合、実際のDBに反映するためには以下のコマンドを実行する必要があります。
  - macの場合
  - `sh script/migrate_db.sh`
  - windowsの場合
  - `script\migrate_db.bat`
- このコマンドは、DBのすべてのデータを削除します今DBに存在するデータを`api/db_back_up/`にバックアップされます。

### frontend
基本的には`frontend`ディレクトリのファイルを編集して開発を進めていきます。
- `frontend`ディレクトリの構成は以下の通りです。
  - `frontend`
      - `css/*`: CSSファイルを置きます。
      - `js/*`: JavaScriptファイルを置きます。
        - `api.js`: APIを呼び出す関数を定義するファイルを置きます。
      - `*****.html`: ページごとのHTMLファイルを置きます。


## よく使うコマンドについて
コピペって使ってください。

### プロジェクトの起動
1. `cd`
2. `cd Desktop`
3. `cd myj-fastapi-web-app-main`
4. `docker-compose up`

### テーブル構造の変更をDBに反映
macの場合: `sh script/migrate_db.sh`

windowsの場合: `script\migrate_db.bat`

### 新しいパッケージの追加
macの場合: `sh script/add-package.sh <パッケージ名>`

windowsの場合: `script\add-package.bat <パッケージ名>`

## FQA
## Q1: Windowsにおいて、`cd Desktop`でエラーが出る

Windowsの場合、OneDriveの関係でDesktopが存在しない場合があります。

その場合、`cd OneDrive`で移動して`dir`でディレクトリの一覧を確認しながら、`Desktop`か`デスクトップ`に移動してください。

## Q2: フロントエンドでAPIを呼び出すと422エラーが出る
422は、リクエストの形式が正しくない場合に出るエラーです。以下の点を確認してください。

- API側で定義とた通りのリクエストを送っているか。
  - `http://localhost:8000/docs` でAPIの仕様を確認できます。
  - NOTE: JSONは末尾のカンマはを含めるとエラーになるので注意してください。この記事も参考にしてください。
    - [JSONの末尾のカンマにご用心](https://plugout.hateblo.jp/entry/2024/02/01/000000)

- `fetch`の第2引数に`{ body: JSON.stringify(data) }`を指定している場合、`headers: { 'Content-Type': 'application/json' }` の指定が必要です。

## Q3: API呼び出しが500で、エラーログが `pymysql.err.ProgrammingError: (1146, "xxxx doesn't exist")`というエラーが出る
`models/`に定義した内容がDBに反映されていない可能性があります。マイグレーションスクリプトを実行してみてください。

macの場合: `sh script/migrate_db.sh`

windowsの場合: `script\migrate_db.bat`

## Q4: API呼び出しが500で、エラーログが `pydantic.error_wrappers.ValidationError: xxx validation error for xxxxxx` と出る
![20240606124924](https://raw.githubusercontent.com/KuroiCc/kuroi-image-host/main/images/20240606124924.png)

`response_model`で指定しているスキーマを正く作ることができませんでした、このエラーメッセージの場合は、`title`が欠けていると書いています。

FastAPIはDBの結果のラベルを探して、スキーマで定義した変数名と一致するラベルの値でスキーマを作ります。そのため、DBの結果のラベルとスキーマの変数名を一致させる必要があります。

以下のやり方で、DBの結果のラベルを確認することができます。違ったラベルがある場合はスキーマの変数名を変更するか、`.label("xxxx")`でラベルを変更してください。

```python
# api/cruds/task.py の get_multiple_tasks_with_done 関数を例に
def get_multiple_tasks_with_done(
    db: Session,
    user_id: int,
) -> list[Row]:
    result: Result = db.execute(
        select(
            task_model.Task.id,
            task_model.Task.title,
            task_model.Task.due_date,
            task_model.Task.user_id,
            task_model.Done.id.isnot(None).label("done"),
        )
        .filter(task_model.Task.user_id == user_id)
        .outerjoin(task_model.Done)
    )

    all_result = result.all()
    print("ラベルがつきの結果をdictの形でprintする")
    for row in all_result:
        print(row._asdict())

    return all_result
```

## Q5: なんかDBにいる正いデータをAPIから返してくれない。

[前のQ](#q-apiの呼び出しはpymysqlerrprogrammingerror-1146-xxxx-doesnt-existというエラーが出る)と同じ状況かもしれないので、とりあえずラベルをチェックしてみてください。

## Q6: DBを操作するすべてのAPI呼び出しが500で、エラーログが `sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize....` と出る

![20240613170715](https://raw.githubusercontent.com/KuroiCc/kuroi-image-host/main/images/20240613170715.png)

ここに注目、

> When initializing mapper Mapper[**Task(tasks)**], expression 'Memo' failed to locate a name ('**Memo**').

一般的には `Task` テーブルに `relationship("Memo", ...)` を使ったけど、`Memo` テーブルの定義が見つからないというエラーです。`api/models/memo.py` とかに定義はしたが、最終的には `main.py` からみて `Memo` がimportされてない場合もこのエラーが出ます。

NOTE: 普通はmain.pyでimport router -> routerでimport crud -> crudでimport model という流れでimportされる。

```python
class Task(Base):
    ...
    memo = relationship("Memo", back_populates="task", cascade="delete")
```

`memo = relationship("Memo", ...)` を一時的にコメントアウトすると、うまくいけます。


## 備考
prj全体の構造は[`docs/prj-overview.md`](docs/prj-overview.md)を参照してください。

TASAとこのでもアプリ自体を開発する人は必ず読んでください。
