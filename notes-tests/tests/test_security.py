"""Хеширование паролей."""
from backend import security  # модуль, который шифрует и проверяет пароли


def test_right_password():  # правильный пароль подходит
    stored = security.hash_password("password123")  # превращаем пароль в хеш (так он хранится в базе)
    assert security.verify_password("password123", stored) is True  # тот же пароль совпадает с хешем


def test_wrong_password():  # неправильный пароль не подходит
    stored = security.hash_password("password123")  # хеш настоящего пароля
    assert security.verify_password("other", stored) is False  # другой пароль не совпадает


def test_password_not_stored_as_is():  # пароль не хранится открытым текстом
    assert "password123" not in security.hash_password("password123")  # в хеше нет самого пароля


def test_broken_hash():  # испорченный хеш не ломает проверку
    assert security.verify_password("x", "мусор") is False  # хеш вообще не в том формате
    assert security.verify_password("x", "scrypt$zz$00") is False  # формат похож, но соль «zz» — не hex
