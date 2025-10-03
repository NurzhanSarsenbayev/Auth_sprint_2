import pytest
from django.urls import reverse
from movies.models import Filmwork


@pytest.mark.django_db
def test_admin_search_by_title(logged_client):
    """Поиск по названию фильма"""
    Filmwork.objects.create(title="Searchable Movie", type="movie")
    Filmwork.objects.create(title="Hidden Film", type="movie")

    url = reverse("admin:movies_filmwork_changelist")
    resp = logged_client.get(url, {"q": "Searchable"})
    content = resp.content.decode()

    assert "Searchable Movie" in content
    assert "Hidden Film" not in content


@pytest.mark.django_db
def test_admin_filter_by_type(logged_client):
    """Фильтр фильмов по типу"""
    Filmwork.objects.create(title="Movie One", type="movie")
    Filmwork.objects.create(title="Show One", type="tv_show")

    url = reverse("admin:movies_filmwork_changelist")
    resp = logged_client.get(url, {"type": "movie"})
    content = resp.content.decode()

    assert "Movie One" in content
    assert "Show One" not in content


@pytest.mark.django_db
def test_admin_search_and_filter_combined(logged_client):
    """Комбинация поиска и фильтра"""
    Filmwork.objects.create(title="Epic Movie", type="movie")
    Filmwork.objects.create(title="Epic Show", type="tv_show")

    url = reverse("admin:movies_filmwork_changelist")
    resp = logged_client.get(url, {"q": "Epic", "type": "movie"})
    content = resp.content.decode()

    # должно остаться только кино
    assert "Epic Movie" in content
    assert "Epic Show" not in content


@pytest.mark.django_db
def test_admin_sorting_by_rating(logged_client):
    """Проверяем сортировку фильмов по рейтингу"""
    Filmwork.objects.create(title="Low Rated", type="movie", rating=1.0)
    Filmwork.objects.create(title="High Rated", type="movie", rating=9.5)

    url = reverse("admin:movies_filmwork_changelist")

    # сортировка по рейтингу по убыванию
    resp = logged_client.get(url, {"o": "-4"})
    # "o" = order_by, в админке поле rating = 4-й индекс (см. list_display)
    content = resp.content.decode()

    first_pos = content.find("High Rated")
    second_pos = content.find("Low Rated")
    assert first_pos < second_pos
