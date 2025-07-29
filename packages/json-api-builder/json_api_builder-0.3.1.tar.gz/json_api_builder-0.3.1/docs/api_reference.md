# APIリファレンス

`json-api-builder` の `AppBuilder` によって自動生成されるAPIエンドポイントの仕様について詳述します。

## リソースの登録 `add_resource`

`builder.add_resource()` メソッドでリソースを登録すると、CRUD操作のためのエンドポイントが自動的に作成されます。

```python
builder.add_resource(
    model: type[SQLModel],
    create_schema: type[SQLModel] | None = None,
    update_schema: type[SQLModel] | None = None,
    path: str | None = None,
)
```

-   **`model`**: データベースとAPIの基本となる `SQLModel` クラス。
-   **`create_schema`**: (任意) アイテム作成時に使用するバリデーションスキーマ。指定しない場合は `model` が使われます。
-   **`update_schema`**: (任意) アイテム更新時に使用するバリデーションスキーマ。指定しない場合は `model` が使われます。
-   **`path`**: (任意) ���ンドポイントのURLパス。指定しない場合は、モデルのテーブル名（例: `Hero` -> `/heroes`）から自動生成されます。

---

## CRUDエンドポイント

`builder.add_resource(model=Hero, path="/heroes")` のようにリソースを登録した場合の例です。

### `POST /heroes/`

新しいアイテムを作成します。

-   **説明**: リクエストボディで受け取ったデータを使用して、新しいアイテムをデータベースに保存します。
-   **リクエストボディ**:
    -   **Content-Type**: `application/json`
    -   **スキーマ**: `add_resource` に渡された `create_schema`（デフォルトでは `model`）。
-   **成功レスポンス**:
    -   **ステータスコード**: `200 OK`
    -   **内容**: データベースに作成されたアイテムのデータ（`id` を含む）。
-   **エラーレスポンス**:
    -   **ステータスコード**: `422 Unprocessable Entity` - リクエストボディがスキーマのバリデーションに失敗した場合。

---

### `GET /heroes/`

アイテムのリストを取得します。フィルタリ��グとページネーションに対応しています。

-   **説明**: 条件に一致するアイテムのリストを返します。
-   **クエリパラメータ**:
    -   **フィルタリング**: モデルのフィールド名をクエリパラメータとして使用することで、そのフィールドが特定の値と一致するアイテムを絞り込めます。（例: `?age=30&name=Spider-Boy`）
    -   **ページネーション**:
        -   `limit` (integer, optional, default: 50): 一度に取得するアイテムの最大数を指定します。
        -   `offset` (integer, optional, default: 0): 先頭からスキップするアイテムの数を指定します。
-   **成功レスポンス**:
    -   **ステータスコード**: `200 OK`
    -   **内容**: `data`（アイテムのリスト）と `total`（フィルタ条件に一致した総件数）を含むオブジェクト。
        ```json
        {
          "data": [
            {
              "name": "Deadpond",
              "secret_name": "Dive Wilson",
              "age": 12,
              "id": 1
            }
          ],
          "total": 1
        }
        ```

---

### `GET /heroes/{item_id}`

指定されたIDのアイテムを1件取得します。

-   **パスパラメータ**:
    -   `item_id` (integer, required): 取得したいアイテムのID。
-   **成功レスポンス**:
    -   **ステータスコード**: `200 OK`
    -   **内容**: 対応するアイテムのデータ。
-   **エラーレスポンス**:
    -   **ステータスコード**: `404 Not Found` - 指定されたIDのアイテムが存在しない場合。

---

### `PATCH /heroes/{item_id}`

指定されたIDのアイテムを部分的に更新します。

-   **パスパラメータ**:
    -   `item_id` (integer, required): 更新したいアイテムのID。
-   **リクエストボディ**:
    -   **スキーマ**: `add_resource` に渡された `update_schema`（デフォルトでは `model`）。更新したいフィールドのみを含めます。
-   **成功レスポンス**:
    -   **ステータスコード**: `200 OK`
    -   **内容**: 更新後のアイテムデータ。
-   **エラーレスポンス**:
    -   **ステータスコード**: `404 Not Found` - 指定されたIDのアイテムが存在しない場合。

---

### `DELETE /heroes/{item_id}`

指定されたIDのアイテムを削除します。

-   **パスパラメータ**:
    -   `item_id` (integer, required): 削除したいアイテムのID。
-   **成功レスポンス**:
    -   **ステータスコード**: `200 OK`
    -   **内容**: 削除されたアイテムのデータ。
-   **エラーレスポンス**:
    -   **ステータスコード**: `404 Not Found` - 指定されたIDのアイテムが存在しない場合。