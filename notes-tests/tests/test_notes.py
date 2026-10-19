"""Заметки: создание, список, изменение, удаление."""
from fastapi.testclient import TestClient  # нужен, чтобы создать второго пользователя в отдельном «браузере»

from backend import main  # само приложение


def test_new_user_has_welcome_note(user):  # новому пользователю создаётся приветственная заметка
    notes = user.get("/api/notes").json()  # получаем список заметок
    assert len(notes) == 1  # заметка ровно одна
    assert notes[0]["pinned"] is True  # и она закреплена


def test_create_note(user):  # можно создать заметку
    r = user.post("/api/notes", json={"title": "Купить", "body": "молоко"})  # отправляем заголовок и текст
    assert r.status_code == 201  # 201 = «создано»
    assert r.json()["title"] == "Купить"  # заголовок сохранился
    assert r.json()["body"] == "молоко"  # текст сохранился


def test_created_note_appears_in_list(user):  # новая заметка видна в списке
    user.post("/api/notes", json={"title": "Купить"})  # создаём заметку
    titles = [n["title"] for n in user.get("/api/notes").json()]  # собираем заголовки всех заметок
    assert "Купить" in titles  # наша заметка среди них


def test_tags_are_cleaned(user):  # теги чистятся: без пробелов, маленькими буквами, без повторов и пустых
    r = user.post("/api/notes", json={"tags": [" Работа ", "работа", ""]})  # передаём «грязные» теги
    assert r.json()["tags"] == ["работа"]  # остался один чистый тег


def test_wrong_color(user):  # нельзя указать несуществующий цвет
    r = user.post("/api/notes", json={"color": "black"})  # чёрного цвета в приложении нет
    assert r.status_code == 422  # 422 = «неверные данные»


def test_pinned_and_archived_together(user):  # заметка не может быть одновременно закреплена и в архиве
    r = user.post("/api/notes", json={"pinned": True, "archived": True})  # ставим обе галки
    assert r.status_code == 422  # сервер отказывает


def test_update_note(user):  # можно изменить заметку
    note = user.post("/api/notes", json={"title": "старый"}).json()  # создаём заметку и запоминаем её
    r = user.patch(f"/api/notes/{note['id']}", json={"title": "новый"})  # меняем заголовок по id
    assert r.status_code == 200  # 200 = «ок»
    assert r.json()["title"] == "новый"  # заголовок поменялся


def test_delete_and_restore_note(user):  # заметку можно удалить и вернуть обратно
    note = user.post("/api/notes", json={"title": "удали меня"}).json()  # создаём заметку

    assert user.delete(f"/api/notes/{note['id']}").status_code == 204  # удаляем, 204 = «ок, ответ пустой»
    titles = [n["title"] for n in user.get("/api/notes").json()]  # заголовки оставшихся заметок
    assert "удали меня" not in titles  # удалённой заметки в списке нет

    assert user.post(f"/api/notes/{note['id']}/restore").status_code == 200  # восстанавливаем
    titles = [n["title"] for n in user.get("/api/notes").json()]  # снова берём заголовки
    assert "удали меня" in titles  # заметка вернулась


def test_unknown_note(user):  # нельзя изменить заметку, которой нет
    assert user.patch("/api/notes/nope", json={"title": "x"}).status_code == 404  # 404 = «не найдено»


def test_notes_without_login(client):  # без входа заметки не отдаются
    assert client.get("/api/notes").status_code == 401  # 401 = «нужно войти»


def test_other_user_cannot_see_my_notes(user):  # чужие заметки не видны и не меняются
    note = user.post("/api/notes", json={"title": "секрет"}).json()  # alice создаёт заметку

    bob = TestClient(main.app)  # второй «браузер» со своими cookie
    bob.post("/api/auth/register", json={"username": "bob", "password": "password123"})  # регистрируем bob

    titles = [n["title"] for n in bob.get("/api/notes").json()]  # заголовки заметок bob
    assert "секрет" not in titles  # заметки alice у bob нет
    assert bob.patch(f"/api/notes/{note['id']}", json={"title": "взлом"}).status_code == 404  # изменить чужую заметку bob не может
