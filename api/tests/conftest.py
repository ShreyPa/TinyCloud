import os
import pytest
from main import app, get_db_connection


@pytest.fixture
def test_db(monkeypatch):

    monkeypatch.setenv("DB_NAME", "tinycloud_test")

    assert os.getenv("DB_NAME") == "tinycloud_test"

    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            database_name = cursor.fetchone()[0]

        assert database_name == "tinycloud_test"

        conn.commit()

    finally:
        conn.close()
    yield

    conn = get_db_connection()

    try:
      with conn.cursor() as cursor:
        cursor.execute("DELETE FROM apps")

        conn.commit()
    finally:
      conn.close()

@pytest.fixture
def client(test_db):
    app.config["TESTING"] = True
    return app.test_client()