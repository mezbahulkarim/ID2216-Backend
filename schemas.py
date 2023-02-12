from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str
    email: str

    class Config:
        orm_mode = True


class Movie_Search(BaseModel):
    title: str
    image_url: str
    link: str
    id: str

    class Config:
        orm_mode = True


class Movie_Detail(BaseModel):
    title: str
    release_date: str
    image_url: str
    genre: str
    length: str
    description: str
    actors: list
    director: str
    screenplay: str
    link: str
    id: str

    class Config:
        orm_mode = True


class Game_Search(BaseModel):
    title: str
    image_url: str
    link: str
    id: str

    class Config:
        orm_mode = True


class Game_Detail(BaseModel):
    title: str
    image_url: str
    description: str
    release_date: str
    developer: str
    publisher: str
    genres: list
    link: str
    # game_id: int

    class Config:
        orm_mode = True


class Book_Search(BaseModel):
    title: str
    image_url: str
    link: str
    id: str

    class Config:
        orm_mode = True


class Book_Detail(BaseModel):
    title: str
    author: str
    image_url: str
    description: str
    publication_info: str
    genres: list
    pages: str
    link: str
    id: str

    class Config:
        orm_mode = True


class Wishlist(BaseModel):
    # wishlist_id: int
    media_id: str
    media_type: str
    username: str

    class Config:
        orm_mode = True


class Library(BaseModel):
    # wishlist_id: int
    media_id: str
    media_type: str
    username: str

    class Config:
        orm_mode = True


class Progress_Books(BaseModel):

    media_id: str
    hours_read: Optional[str] = None
    rating: Optional[str] = None
    notes: Optional[str] = None
    pages_read: Optional[str] = None

    class Config:
        orm_mode = True


class Progress_Games(BaseModel):

    media_id: str
    hours_played: Optional[str] = None
    rating: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True


class Progress_Movies(BaseModel):

    media_id: str
    hours_watched: Optional[str] = None
    rating: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True
