"""Сервер отдаёт фронтенд."""


def test_main_page(client):  # главная страница открывается
    r = client.get("/")  # открываем корень сайта
    assert r.status_code == 200  # 200 = «ок»
    assert "<title>Заметки</title>" in r.text  # это действительно страница приложения «Заметки»


def test_static_files(client):  # файлы фронтенда отдаются
    for path in ["/app.js", "/api.js", "/styles.css"]:  # перебираем скрипты и стили
        assert client.get(path).status_code == 200, path  # каждый файл открывается; при ошибке покажет, какой именно
