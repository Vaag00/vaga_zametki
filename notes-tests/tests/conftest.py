"""Общие заготовки для тестов.

Каждый тест получает свою пустую базу во временной папке,
поэтому настоящий backend/notes.db не трогается.
"""
import pytest  # библиотека для тестов
from fastapi.testclient import TestClient  # «браузер», который шлёт запросы к приложению без запуска сервера

from backend import db, main  # db — работа с базой, main — само приложение FastAPI


@pytest.fixture  # фикстура: pytest сам создаст её и передаст в тест, у которого есть параметр client
def client(tmp_path, monkeypatch):  # tmp_path — временная папка, monkeypatch — подмена значений на время теста
    """Клиент (как браузер) с чистой базой."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")  # подменяем путь к базе на временный файл
    with TestClient(main.app) as c:  # with запускает приложение (и создаёт таблицы в базе)
        yield c  # отдаём клиента тесту; после теста приложение остановится


@pytest.fixture  # ещё одна фикстура, она использует client
def user(client):  # client pytest создаст сам из фикстуры выше
    """Клиент, в котором уже зарегистрирован и залогинен пользователь alice."""
    client.post("/api/auth/register", json={"username": "alice", "password": "password123"})  # регистрируем alice (после этого она сразу залогинена)
    return client  # возвращаем того же клиента, но уже с cookie входа
