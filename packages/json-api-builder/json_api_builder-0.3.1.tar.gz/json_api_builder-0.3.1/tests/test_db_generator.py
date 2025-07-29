# tests/test_db_generator.py
import json
import shutil
from pathlib import Path

import pytest
from sqlmodel import Field, Session, SQLModel, create_engine, select

from json_api_builder import generate_db_from_json_file


# --- 1. テスト用のモデル定義 ---
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int


# --- 2. テスト用のセットアップフィクスチャ ---
@pytest.fixture
def test_artifacts_setup():
    artifacts_dir = Path(__file__).parent / "test_artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    db_path = artifacts_dir / "test.db"
    json_path = artifacts_dir / "users.json"

    yield str(db_path), str(json_path)

    shutil.rmtree(artifacts_dir)


# --- 3. テストケース ---
def test_generate_from_json_file(test_artifacts_setup):
    db_path, json_path = test_artifacts_setup

    # Setup JSON file with an array of users
    users_data = [
        {"name": "Alice", "age": 30},
        {"id": 99, "name": "Bob", "age": 25},  # 'id' should be ignored
        {"name": "Charlie", "age": 35},
    ]
    with open(json_path, "w") as f:
        json.dump(users_data, f)

    # Generate database
    generate_db_from_json_file(
        model=User,
        db_path=db_path,
        json_path=json_path,
        overwrite=True,
    )

    # Verify database content
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        users = session.exec(select(User).order_by(User.id)).all()

        assert len(users) == 3

        # Verify auto-incrementing IDs
        assert users[0].id == 1
        assert users[0].name == "Alice"

        assert users[1].id == 2
        assert users[1].name == "Bob"  # Original id: 99 is ignored

        assert users[2].id == 3
        assert users[2].name == "Charlie"

    engine.dispose()


def test_generate_from_invalid_json(test_artifacts_setup):
    db_path, json_path = test_artifacts_setup

    # Setup JSON file with an object instead of an array
    with open(json_path, "w") as f:
        json.dump({"1": {"name": "Alice"}}, f)

    with pytest.raises(TypeError, match="JSON file must contain a list of records."):
        generate_db_from_json_file(
            model=User,
            db_path=db_path,
            json_path=json_path,
        )
