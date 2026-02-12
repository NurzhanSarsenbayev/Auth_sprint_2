from models.film_short import FilmShort
from models.genre import Genre
from models.person import Person
from pydantic import BaseModel


class SearchResults(BaseModel):
    films: list[FilmShort] = []
    persons: list[Person] = []
    genres: list[Genre] = []
