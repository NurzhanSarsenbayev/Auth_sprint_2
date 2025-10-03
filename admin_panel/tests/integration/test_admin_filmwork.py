import pytest
from django.urls import reverse
from movies.models import Filmwork, Genre, Person, PersonRole


@pytest.mark.django_db
def test_admin_filmwork_crud(logged_client):
    """CRUD для фильмов через админку"""

    # ➕ Добавляем фильм
    add_url = reverse("admin:movies_filmwork_add")
    resp = logged_client.post(
        add_url,
        {
            "title": "Test Movie",
            "type": "movie",
            "rating": "8.5",
            # 👇 пустые inline формы
            "genrefilmwork_set-INITIAL_FORMS": "0",
            "genrefilmwork_set-TOTAL_FORMS": "0",
            "personfilmwork_set-INITIAL_FORMS": "0",
            "personfilmwork_set-TOTAL_FORMS": "0",
        },
        follow=True,
    )

    assert resp.status_code == 200
    assert Filmwork.objects.filter(title="Test Movie").exists()

    # ✏️ Редактируем фильм
    film = Filmwork.objects.get(title="Test Movie")
    change_url = reverse("admin:movies_filmwork_change", args=[film.id])
    resp = logged_client.post(
        change_url,
        {
            "title": "Updated Movie",
            "type": "tv_show",
            "rating": "9.0",
            "genrefilmwork_set-INITIAL_FORMS": "0",
            "genrefilmwork_set-TOTAL_FORMS": "0",
            "personfilmwork_set-INITIAL_FORMS": "0",
            "personfilmwork_set-TOTAL_FORMS": "0",
        },
        follow=True,
    )
    assert resp.status_code == 200
    film.refresh_from_db()
    assert film.title == "Updated Movie"
    assert film.type == "tv_show"

    # ❌ Удаляем фильм
    delete_url = reverse("admin:movies_filmwork_delete", args=[film.id])
    resp = logged_client.post(delete_url, {"post": "yes"}, follow=True)
    assert resp.status_code == 200
    assert not Filmwork.objects.filter(id=film.id).exists()


@pytest.mark.django_db
def test_admin_filmwork_inlines(logged_client):
    """Добавление фильма с жанром и персоной через inline"""

    genre = Genre.objects.create(name="Comedy")
    person = Person.objects.create(full_name="Jane Doe")

    add_url = reverse("admin:movies_filmwork_add")
    resp = logged_client.post(
        add_url,
        {
            "title": "Inline Film",
            "type": "movie",
            "rating": "6.5",
            # inline жанры
            "genrefilmwork_set-INITIAL_FORMS": "0",
            "genrefilmwork_set-TOTAL_FORMS": "1",
            "genrefilmwork_set-0-genre": genre.id,
            # inline персоны
            "personfilmwork_set-INITIAL_FORMS": "0",
            "personfilmwork_set-TOTAL_FORMS": "1",
            "personfilmwork_set-0-person": person.id,
            "personfilmwork_set-0-role": PersonRole.ACTOR,
        },
        follow=True,
    )
    assert resp.status_code == 200
    film = Filmwork.objects.get(title="Inline Film")
    assert film.genres.filter(id=genre.id).exists()
    assert film.persons.filter(id=person.id).exists()
