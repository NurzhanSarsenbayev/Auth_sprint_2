import pytest
from movies.models import (Genre,
                           Person,
                           Filmwork,
                           FilmworkType,
                           GenreFilmwork,
                           PersonFilmwork,
                           PersonRole)


@pytest.mark.django_db
def test_genre_str():
    genre = Genre.objects.create(name="Comedy")
    assert str(genre) == "Comedy"


@pytest.mark.django_db
def test_person_str():
    person = Person.objects.create(full_name="Tom Hanks")
    assert str(person) == "Tom Hanks"


@pytest.mark.django_db
def test_filmwork_str_and_type():
    film = Filmwork.objects.create(title="Inception", type=FilmworkType.MOVIE)
    assert str(film) == "Inception"
    assert film.type == FilmworkType.MOVIE


@pytest.mark.django_db
def test_genre_filmwork_unique(db):
    film = Filmwork.objects.create(title="Matrix")
    genre = Genre.objects.create(name="Sci-Fi")
    GenreFilmwork.objects.create(filmwork=film, genre=genre)
    with pytest.raises(Exception):
        GenreFilmwork.objects.create(filmwork=film, genre=genre)


@pytest.mark.django_db
def test_person_filmwork_unique(db):
    film = Filmwork.objects.create(title="Avatar")
    person = Person.objects.create(full_name="James Cameron")
    PersonFilmwork.objects.create(
        filmwork=film,
        person=person,
        role=PersonRole.DIRECTOR
    )
    with pytest.raises(Exception):
        PersonFilmwork.objects.create(
            filmwork=film,
            person=person,
            role=PersonRole.DIRECTOR
        )
