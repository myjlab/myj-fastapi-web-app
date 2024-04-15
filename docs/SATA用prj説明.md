# インフラ構成

```mermaid
graph LR
    subgraph Docker
        A["Frontendコンテナ\n(HTML,CSS,JSをhosting)"]
        D[(MySQLコンテナ)]

        subgraph FastAPIコンテナ
        direction TB
        R[FastAPIルート]
        ST["静的ファイル\n(/staticに)\n(画像など)"]
        end
    end

    

  B((Browser)) -- Port 3000 --> A
  B -- Port 8000 --> R
  B -- Port 8000 --> ST
  R -- Port 3306 --> D

  VSC[VSCode DBプラグイン] -- Port 33306 --> D

```

# アプリケーション構成
## api
### モジュール依存関係
```mermaid
graph TB
    MAIN["`**FastAPIの入口**
    fa:fa-file-code *api/main.py*`"]

    ROUTE["`**ルーティング**
    fa:fa-file-code *api/routers/**`"]

    SCHEMA["`**API通信スキーマ**
    fa:fa-file-code *api/schemas/**`"]

    MODEL["`**DBモデル(テーブル構造)**
    fa:fa-file-code *api/models/**`"]

    DB["`**DBインフラ**
    fa:fa-file-code *api/db.py*`"]

    CRUD["`**CRUD操作**
    fa:fa-file-code *api/crud/**`"]

    subgraph extra_modules
        AUTH["`**認証**
        fa:fa-file-code *api/extra_modules/auth/**`"]

        IMAGE["`**画像操作**
        fa:fa-file-code *api/extra_modules/image/**`"]
    end

    MAIN　--> ROUTE
    ROUTE　--> SCHEMA
    ROUTE　--> CRUD
    ROUTE　--> AUTH
    ROUTE　--> DB
    ROUTE  --> IMAGE
    MODEL --> DB
    CRUD --> DB
    CRUD --> MODEL
    CRUD --> SCHEMA
```

### モジュール
- **FastAPIの入口**, `api/main.py`
  - FastAPIのインスタンスを作成し、ルーティングを読み込む
  - /staticに静的ファイルのホスティング
  - CORSのミドルウェア
- **ルーティング**, `api/routers/**`
  - ルーティングの定義
  - HTTPからデータを受け取り、CRUD操作に委譲
  - CRUD操作の結果を返す、適切なHTTPエラーを返す
- **API通信スキーマ**, `api/schemas/**`
  - ルーティングで受け取るデータの形を定義
  - ルーティングで返すデータのスキーマ
- **CRUD操作**, `api/crud/**`
  - クエリでDBデータを返す
  - ルーティングで受け取ったデータでDBを操作
    - 基本的に`schemas`を`models`に変換し、`db`に反映
- **DBモデル(テーブル構造)**, `api/models/**`
  - DBのテーブル構造を定義
- **DBインフラ**, `api/db.py`
  - DBの接続情報を定義
  - DBのセッションを管理
- **extra_modules**
  - **基本的に学生は気にしなくていい、使用するだけ**
  - **認証**, `api/extra_modules/auth/**`
    - ユーザー認証に関する処理
  - **画像操作**, `api/extra_modules/image/**`
    - 画像のアップロードを受け保存する

### DB構造
```mermaid
erDiagram
    User ||--o{ Task : "has"
    Task ||--o| Done : "status"
    User {
        int id PK "Primary Key"
        string email "Unique, Not Null"
        string nickname "Optional"
        string password "Not Null"
    }
    Task {
        int id PK "Primary Key"
        string title "Not Null"
        date due_date "Optional"
        string img_path "Optional"
        int user_id FK "Foreign Key"
    }
    Done {
        int id PK, FK "Primary Key, Foreign Key"
    }

```

### API構造
(WIP)

## frontend
(WIP)

# スクリプト
(WIP)

# テストについて
(WIP)