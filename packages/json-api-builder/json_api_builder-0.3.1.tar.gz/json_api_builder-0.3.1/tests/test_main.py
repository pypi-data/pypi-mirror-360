# tests/test_main.py
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import Field, SQLModel

from json_api_builder import AppBuilder


# --- 1. テスト用のモデル定義 ---
class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None


# --- 2. 非同期HTTPクライアントのフィクスチャ ---
@pytest_asyncio.fixture(name="client")
async def client_fixture() -> AsyncClient:
    # 各テストごとに完全に独立したインメモリDBを使用
    test_database_url = "sqlite+aiosqlite:///:memory:"

    builder = AppBuilder(db_path=test_database_url)
    builder.add_resource(Hero, path="/heroes")

    app = builder.get_app()

    # テーブルを作成
    async with builder.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # テーブルを削除
    async with builder.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# --- 3. テストケース ---
@pytest.mark.asyncio
async def test_full_crud_cycle(client: AsyncClient):
    # Create
    response = await client.post(
        "/heroes",
        json={"name": "Deadpond", "secret_name": "Dive Wilson", "age": 12},
    )
    assert response.status_code == 200

    # Read (to get the created item with its ID)
    response = await client.get("/heroes")
    assert response.status_code == 200
    all_heroes = response.json()["data"]
    assert len(all_heroes) == 1
    hero = all_heroes[0]
    assert hero["name"] == "Deadpond"
    hero_id = hero["id"]

    # Read One
    response = await client.get(f"/heroes/{hero_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Deadpond"

    # Update
    response = await client.patch(f"/heroes/{hero_id}", json={"name": "Updated"})
    assert response.status_code == 200
    # Verify update by reading again
    response = await client.get(f"/heroes/{hero_id}")
    assert response.json()["name"] == "Updated"

    # Delete
    response = await client.delete(f"/heroes/{hero_id}")
    assert response.status_code == 200

    # Verify Deletion
    response = await client.get(f"/heroes/{hero_id}")
    assert response.status_code == 404
