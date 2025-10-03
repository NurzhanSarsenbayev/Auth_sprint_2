import uuid
from django.db import models


class TimeStampedModel(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "content_genre"
        ordering = ["name"]

    def __str__(self): return self.name


class Person(TimeStampedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)

    class Meta:
        db_table = "content_person"
        ordering = ["full_name"]

    def __str__(self): return self.full_name


class FilmworkType(models.TextChoices):

    MOVIE = "movie", "Movie"
    TV_SHOW = "tv_show", "TV Show"


class Filmwork(TimeStampedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    type = models.CharField(
        max_length=20,
        choices=FilmworkType.choices,
        default=FilmworkType.MOVIE)

    genres = models.ManyToManyField(Genre, through="GenreFilmwork")
    persons = models.ManyToManyField(Person, through="PersonFilmwork")

    class Meta:
        db_table = "content_filmwork"
        ordering = ["-creation_date", "title"]

    def __str__(self): return self.title


class GenreFilmwork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filmwork = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content_genre_filmwork"
        unique_together = ("filmwork", "genre")


class PersonRole(models.TextChoices):
    ACTOR = "actor", "Actor"
    DIRECTOR = "director", "Director"
    WRITER = "writer", "Writer"


class PersonFilmwork(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filmwork = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=PersonRole.choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content_person_filmwork"
        unique_together = ("filmwork", "person", "role")
