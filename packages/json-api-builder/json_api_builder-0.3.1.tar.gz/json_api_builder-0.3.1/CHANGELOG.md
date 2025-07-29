# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-07-03

### Changed
- **アーキテクチャの全面刷新**: プロジェクトの核心を、実績のあるライブラリである `SQLModel` と `FastCRUD` を活用する形に完全に移行。
  - 自作の `APIBuilder` を、`fastcrud` をラップする、よりシンプルで堅牢な `AppBuilder` に置き換え。
  - PydanticモデルとSQLAlchemyモデルの二重管理を廃止��、`SQLModel` に一本化。
  - これにより、コードが大幅に簡素化され、安定性が劇的に向上。
- **テストの再構築**: `pytest-asyncio` を導入し、非同期アプリケーションに対するテストのベストプラクティスを適用。これにより、これまでのテストで発生していたすべての問題（`PermissionError`, `TypeError`など）を根本的に解決。
- **ドキュメントの抜本的見直し**: `README.md` を、新しいアーキテクチャの使い方、Renderへのデプロイ方法、安全なデータ管理方法を反映した、実践的な内容に全面的に書き換え。

### Removed
- **ダウンロード機能の廃止**: セキュリティリスクと、より優れた代替手段（SSH/scp）の存在を考慮し、`/download` エンドポイントを廃止。
- 古いサンプルコード (`examples` ディレクトリ) をすべて削除。

## [0.1.1] - 2025-07-01

### Changed
- **設計の簡素化**: 後方互換性を破棄し、ライブラリのコアな責務を明確化。
  - `APIBuilder`はAPIサーバーの構築と実行に専念。
  - `Database`クラスを���止し、その機能を`APIBuilder`に統合。
  - `crud.py`モジュールを廃止し、ロジックを関連モジュールに移動。
  - `JSONExporter`/`Importer`クラスを廃止し、シンプルな関数としてのみ提供。
- **テスト容易性の向上**: `lifespan`イベントを導入し、データベース接続を適切に管理することで、テスト時のファイルロック問題を解決。
- **ドキュメントの更新**: 新しい設計思想に合わせて`README.md`とAPIリファレンスを全面的に更新。

## [0.1.0] - 2025-07-01

### Added
- JSONファイルからデータベースを構築するインポート機能 (`JSONImporter`, `import_database_from_json`) を追加。
- PyPI公開用のGitHub Actionsワークフロー (`python-publish.yml`) を追加。
- `pyupgrade`, `vulture` を導入し、CIにコード品質チェックを統合。
- APIの仕様を記述した `docs/api_reference.md` を作成。
- プロジェクトの設計方針を記述した `README.md` のセクションを追加。

### Changed
- データベース接続のライフサイクル管理を改善し、テストの安定性を向上���
- 依存性の注入（DI）の原則に基づき、`JSONExporter` と `JSONImporter` が `Database` オブジェクトを受け取るようにリファクタリング。
- テストフィクスチャを全面的に見直し、クリーンで管理しやすい構造に改善。
- `mypy` の型チェックエラーを、`# type: ignore` を限定的に使用することで解決。

### Removed
- 古いCIワークフロー (`ci.yml`) を削除し、リリース用のワークフローに一本化。
