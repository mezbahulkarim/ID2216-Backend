from pydantic import BaseModel

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
    release_date : str
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
    
