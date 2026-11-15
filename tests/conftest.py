import pytest

from backend.app import database


@pytest.fixture(scope="session", autouse=True)
def test_database(tmp_path_factory):
    """Use an isolated, initialised SQLite database for the whole test run.

    The tests create TestClient(app) without a context manager, so FastAPI's
    startup event (init_db) never runs. On a fresh CI checkout there is no
    data/structuraai.db, which caused "no such table: inspections".
    """
    data_dir = tmp_path_factory.mktemp("data")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(database, "DATA_DIR", data_dir)
    monkeypatch.setattr(database, "DATABASE_PATH", data_dir / "structuraai.db")

    database.init_db()

    yield

    monkeypatch.undo()
