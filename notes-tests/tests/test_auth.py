"""Регистрация, вход и выход."""


def test_register(client):  # можно зарегистрироваться
    r = client.post("/api/auth/register", json={"username": "alice", "password": "password123"})  # отправляем логин и пароль
    assert r.status_code == 201  # 201 = «создано», регистрация прошла
    assert r.json()["username"] == "alice"  # сервер вернул имя нового пользователя


def test_register_same_username_twice(user):  # нельзя занять уже занятый логин
    r = user.post("/api/auth/register", json={"username": "alice", "password": "password123"})  # alice уже есть, регистрируем ещё раз
    assert r.status_code == 409  # 409 = «конфликт», логин занят


def test_register_short_password(client):  # слишком короткий пароль не принимается
    r = client.post("/api/auth/register", json={"username": "alice", "password": "123"})  # пароль из 3 символов (нужно минимум 8)
    assert r.status_code == 422  # 422 = «неверные данные»


def test_register_bad_username(client):  # слишком короткий логин не принимается
    r = client.post("/api/auth/register", json={"username": "a", "password": "password123"})  # логин из 1 символа (нужно минимум 3)
    assert r.status_code == 422  # 422 = «неверные данные»


def test_me_after_register(user):  # после регистрации сервер знает, кто мы
    r = user.get("/api/auth/me")  # спрашиваем «кто я?»
    assert r.status_code == 200  # 200 = «ок», мы залогинены
    assert r.json()["username"] == "alice"  # сервер узнал alice


def test_me_without_login(client):  # без входа сервер нас не знает
    assert client.get("/api/auth/me").status_code == 401  # 401 = «нужно войти»


def test_login(user):  # можно войти по логину и паролю
    user.post("/api/auth/logout")  # сначала выходим
    r = user.post("/api/auth/login", json={"username": "alice", "password": "password123"})  # входим заново
    assert r.status_code == 200  # вход успешен
    assert user.get("/api/auth/me").status_code == 200  # и сервер снова нас узнаёт


def test_login_wrong_password(user):  # с неверным паролем войти нельзя
    r = user.post("/api/auth/login", json={"username": "alice", "password": "wrong-password"})  # неправильный пароль
    assert r.status_code == 401  # 401 = вход отклонён


def test_login_ignores_username_case(user):  # регистр букв в логине не важен
    r = user.post("/api/auth/login", json={"username": "ALICE", "password": "password123"})  # логин большими буквами
    assert r.status_code == 200  # всё равно пускает


def test_logout(user):  # можно выйти
    assert user.post("/api/auth/logout").status_code == 204  # 204 = «ок, ответ пустой»
    assert user.get("/api/auth/me").status_code == 401  # после выхода сервер нас больше не знает
