import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_admin_login(client, admin_user):
    login_ok = client.login(username="admin", password="adminpass")
    assert login_ok


@pytest.mark.django_db
def test_admin_genre_list(client, admin_user):
    client.login(username="admin", password="adminpass")
    url = reverse("admin:movies_genre_changelist")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_login_page(client):
    """Проверяем, что страница логина доступна"""
    resp = client.get("/admin/login/")
    assert resp.status_code == 200
    assert "Log in" in resp.content.decode()


@pytest.mark.django_db
def test_admin_dashboard_access(logged_client):
    """После логина видим дашборд"""
    resp = logged_client.get("/admin/")
    assert resp.status_code == 200
    assert "Site administration" in resp.content.decode()
