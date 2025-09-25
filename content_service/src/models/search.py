from pydantic import BaseModel
from typing import List
from models.film_short import FilmShort
from models.person import Person
from models.genre import Genre

class SearchResults(BaseModel):
    films: List[FilmShort] = []
    persons: List[Person] = []
    genres: List[Genre] = []
