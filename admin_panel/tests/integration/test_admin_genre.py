import pytest
from django.urls import reverse
from movies.models import Genre


@pytest.mark.django_db
def test_admin_genre_crud(logged_client):
    """CRUD для жанра через админку"""
    # Добавляем жанр
    add_url = reverse("admin:movies_genre_add")
    resp = logged_client.post(add_url, {"name": "Sci-Fi"}, follow=True)
    assert resp.status_code == 200
    assert Genre.objects.filter(name="Sci-Fi").exists()

    # Редактируем жанр
    genre = Genre.objects.get(name="Sci-Fi")
    change_url = reverse("admin:movies_genre_change", args=[genre.id])
    resp = logged_client.post(
        change_url,
        {"name": "Sci-Fi Updated"},
        follow=True)
    assert resp.status_code == 200
    genre.refresh_from_db()
    assert genre.name == "Sci-Fi Updated"

    # Удаляем жанр
    delete_url = reverse("admin:movies_genre_delete", args=[genre.id])
    resp = logged_client.post(delete_url, {"post": "yes"}, follow=True)
    assert resp.status_code == 200
    assert not Genre.objects.filter(id=genre.id).exists()
