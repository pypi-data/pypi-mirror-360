# データベーススキーマ仕様

`json-api-builder` は、データベースのテーブルスキーマを、利用者が定義する **`SQLModel`** から動的に生成します。

## 動的なテーブル生成

このライブラリの核心的な特徴は、あなたが定義した `SQLModel` クラスが、そのままデータベースのテーブル設計図になることです。

`AppBuilder` に `add_resource` メソッドでモデルを追加すると、そのモデルの `__tablename__` に基づいて、対応するテーブルがデータベース内に自動的に作成されます。

### 例

あなたが以下のような `SQLModel` を定義したとします。

```python
from sqlmodel import SQLModel, Field

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
```

このモデルを `builder.add_resource(model=Hero)` のように登録すると、アプリケーションの起動時に、`database.db` ファイル内に以下のようなスキーマを持つ `hero` テーブルが自動的に作成されます。

| カラム名      | データ型     | 制約・属性                               |
|---------------|--------------|------------------------------------------|
| `id`          | `INTEGER`    | プライマリキー, 自動採番                 |
| `name`        | `VARCHAR`    | インデックス付き                         |
| `secret_name` | `VARCHAR`    |                                          |
| `age`         | `INTEGER`    | NULL許容, インデックス付き               |

### 設計思想

このアプローチにより、以下のメリットが生まれます。

-   **単一の信頼できる情報源**: データベースのスキーマとAPIのモデルが単一の `SQLModel` 定義に集約されるため、両者の間に不整合が発生しません。
-   **マイグレーション不要**: モデルのフィールドを追加・変更した場合、アプリケーションを再起動するだけで、データベースのテーブルスキーマが自動的に更新されます（**注意**: これは開発環境での利便性を意図したものであり、本番環境でデータを保持したままスキーマを変更する場合は、Alembicなどの本格的なマイグレーションツールが必要です）。
-   **直感的な開発**: Pythonのクラスを書くだけでデータベースの構造が決まるため、SQLを意識することなく、直感的に開発を進めることができます。
