import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_admin_access_with_admin_role(client, admin_jwt_headers):
    """Админ может зайти в Django admin через /sso/jwt-login"""
    login_url = reverse("sso_login")
    resp = client.get(login_url, **admin_jwt_headers, follow=True)
    assert resp.status_code == 200
    assert "/admin/" in resp.request["PATH_INFO"]

    # теперь сессия есть → доступен index
    url = reverse("admin:index")
    resp = client.get(url)
    assert resp.status_code == 200
    assert ("Django administration" in resp.content.decode()
            or "Администрирование" in resp.content.decode())


@pytest.mark.django_db
def test_admin_access_with_editor_role(client, editor_jwt_headers):
    """Редактор может зайти в админку,
     но без доступа к управлению пользователями"""
    login_url = reverse("sso_login")
    resp = client.get(login_url, **editor_jwt_headers, follow=True)
    assert resp.status_code == 200

    # проверяем доступ к списку пользователей
    user_list_url = reverse("admin:auth_user_changelist")
    resp = client.get(user_list_url)
    # редактор может быть staff, но не superuser → должно быть 403
    assert resp.status_code in (302, 403)


@pytest.mark.django_db
def test_admin_access_with_user_role(client, user_jwt_headers):
    """Обычный пользователь не должен попадать в админку"""
    login_url = reverse("sso_login")
    resp = client.get(login_url, **user_jwt_headers, follow=True)
    # доступ должен быть запрещён
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_guest_redirect_to_login(client):
    """Без токена редирект на стандартный login"""
    url = reverse("admin:index")
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/admin/login/" in resp["Location"]


@pytest.mark.django_db
def test_admin_logout_flow(client, admin_jwt_headers):
    """Админ логинится через JWT, потом выходит и теряет доступ"""

    # Логинимся
    login_url = reverse("sso_login")
    resp = client.get(login_url, **admin_jwt_headers, follow=True)
    assert resp.status_code == 200
    assert "/admin/" in resp.request["PATH_INFO"]

    # Проверяем, что index доступен
    url = reverse("admin:index")
    resp = client.get(url)
    assert resp.status_code == 200

    # Логаут
    logout_url = reverse("sso_logout")
    resp = client.get(logout_url, follow=True)
    assert resp.status_code == 200
    # редиректнуло на /admin/login/
    assert "/admin/login/" in resp.request["PATH_INFO"]

    # Теперь снова доступ к index должен быть закрыт
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/admin/login/" in resp["Location"]


@pytest.mark.django_db
def test_logout_without_login(client):
    """Логаут без сессии всё равно уводит на страницу логина"""
    logout_url = reverse("sso_logout")
    resp = client.get(logout_url, follow=True)
    assert resp.status_code == 200
    assert "/admin/login/" in resp.request["PATH_INFO"]
