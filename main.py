from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import create_client
import jwt 
from passlib.hash import bcrypt
from schemas import *
import models
from database import SessionLocal
from typing import List
from scrapers import *
import json
import asyncio
from typing import Union

db = SessionLocal()

load_dotenv()
app = FastAPI()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")

origins = [
    "http://localhost:2780",
    "http://localhost",
    "https://universal-tracker-web.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase= create_client(url, key)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') 

async def fetch_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms = ['HS256'])
        user_obj = User.parse_obj(payload)

    except:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f'Cannot decode jwt token when fetching authenticated user')

    return user_obj

#User Endpoints
#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.get("/")
def root():
    return "At root, no Path Specified"
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.get("/getallusers", response_model= List[User])
def get_all_users():
    users=db.query(models.User).all()
    return users
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post('/register')
async def register(user: User):

    hashed_password = bcrypt.hash(user.password)
    username = supabase.table('Users').select("*").like('username', user.username).execute()
    email = supabase.table('Users').select("*").like('email', user.email).execute()

    print(username.data)
    print(email.data)

    if username.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
        detail=f'Cannot Register User, Username already Exists')

    if email.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
        detail=f'Cannot Register User, Email already Exists')

    user_entry = supabase.table('Users').insert({"username":user.username, "password": hashed_password, "email": user.email}).execute()
    return {"detail": "OK, Successfully Registered User"}
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = supabase.table('Users').select("*").like('username', form_data.username).execute()
    
    if not user.data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Login Failed, Username does not exist")
    
    password_fetched = user.data[0]['password']
    hashed_password = bcrypt.verify(form_data.password, password_fetched)

    if not hashed_password:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail= f"Login Failed, Passowrd does not match")
  
    token = jwt.encode(user.data[0], JWT_SECRET)
    
    return {'user': user.data[0], 'token': token}       
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = supabase.table('Users').select("*").like('username', form_data.username).execute()
    
    if not user.data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Login Failed, Username does not exist")
    
    password_fetched = user.data[0]['password']
    hashed_password = bcrypt.verify(form_data.password, password_fetched)

    if not hashed_password:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Login Failed, Passowrd does not match")
  
    token = jwt.encode(user.data[0], JWT_SECRET)
    
    return {'access_token': token, 'token_type': 'bearer'}          # return type MUST be of this format, otherwise FastAPI complains
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post('/refreshtoken')
async def refreshtoken(token: str = Depends(oauth2_scheme)):
    return token
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post('/change_username')
async def change_username(username: str, user:User = Depends(fetch_user)):      
    try:
        prev_name = user.username
        changed_record = supabase.table('Users').update({'username': username}).eq('username', prev_name).execute() 
        return {"detail":"OK, successfully changed username"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error changing username")
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post('/change_email')
async def change_email(email: str, user:User = Depends(fetch_user)):          
    try:
        prev_name = user.username
        changed_record = supabase.table('Users').update({'email': email}).eq('username', prev_name).execute() 
        return {"detail":"OK, successfully changed email"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error changing email")
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------
@app.post('/change_password')
async def change_password(password: str, user:User = Depends(fetch_user)):      
    try:
        prev_name = user.username
        hashed_password = bcrypt.hash(password)
        changed_record = supabase.table('Users').update({'password': hashed_password}).eq('username', prev_name).execute() 
        return {"detail":"OK, successfully changed password"}
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error changing password")
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------

# Scraper Endpoints


@app.post('/search_movie')
async def movie_search(search: str, user: User = Depends(fetch_user)):
    try:
        return search_movie(search)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="FAIL, error searching for movie")


@app.post('/search_book')
async def book_search(search: str, user: User = Depends(fetch_user)):
    try:
        return search_book(search)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="FAIL, error searching for book")


@app.post('/search_game')
async def game_search(search: str, user: User = Depends(fetch_user)):
    try:
        return search_game(search)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="FAIL, error searching for game")


@app.post('/detail_movie')
async def movie_detail(search: str, user: User = Depends(fetch_user)):
    try:
        coroutine = asyncio.create_task(detail_movie(search))
        await coroutine
        return_val = coroutine.result()
        # movie: Movie_Detail = return_val
        # return movie
        return return_val
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="FAIL, error getting movie details")


@app.post('/detail_game')
async def game_detail(search: str, user: User = Depends(fetch_user)):
    try:
        return_val = detail_game(search)
        # game: Game_Detail = return_val
        # return game
        return return_val
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="FAIL, error getting game details")
    # NOTES for game_detail- getting this error, POSSIBLY FOR 18+ GAMES:
    # title = page_soup.find('div', class_="apphub_AppName").text.strip()
    # AttributeError: 'NoneType' object has no attribute 'text'


@app.post('/detail_book')
async def book_detail(search: str, user: User = Depends(fetch_user)):
    try:
        return_val = detail_book(search)
        # book: Book_Detail = return_val
        # return book
        return return_val
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="FAIL, error getting book details")


@app.post('/wishlist_add_book')
async def wishlist_add_book(book: Book_Detail, user: User = Depends(fetch_user)):

    books_record = models.Books(
        title=book.title,
        author=book.author,
        image_url=book.image_url,
        description=book.description,
        publication_info=book.publication_info,
        genres=book.genres,
        pages=book.pages,
        link=book.link,
        id=book.id
    )

    if db.query(models.Books).filter(models.Books.id == book.id).first():
        pass

    else:
        db.add(books_record)
        db.commit()

    wishlist_record = models.Wishlist(
        media_id=book.id,
        media_type="Book",
        username=user.username
    )

    if db.query(models.Wishlist).filter(models.Wishlist.username == user.username,
                                        models.Wishlist.media_id == book.id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already added this book to Wishlist")

    else:
        db.add(wishlist_record)
        db.commit()

    return {"detail": "OK, Successfully Added Book to Wishlist"}


@app.post('/wishlist_add_movie')
async def wishlist_add_movie(movie: Movie_Detail, user: User = Depends(fetch_user)):

    movies_record = models.Movies(
        title=movie.title,
        release_date=movie.release_date,
        image_url=movie.image_url,
        genre=movie.genre,
        length=movie.length,
        description=movie.description,
        actors=movie.actors,
        director=movie.director,
        screenplay=movie.screenplay,
        link=movie.link,
        id=movie.id
    )

    if db.query(models.Movies).filter(models.Movies.id == movie.id).first():
        pass

    else:
        db.add(movies_record)
        db.commit()

    wishlist_record = models.Wishlist(
        media_id=movie.id,
        media_type="Movie",
        username=user.username
    )

    if db.query(models.Wishlist).filter(models.Wishlist.username == user.username,
                                        models.Wishlist.media_id == movie.id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already added this movie to Wishlist")

    else:
        db.add(wishlist_record)
        db.commit()

    return {"detail": "OK, Successfully Added Movie to Wishlist"}


@app.post('/library_add_book')
async def library_add_book(book: Book_Detail, user: User = Depends(fetch_user)):

    books_record = models.Books(
        title=book.title,
        author=book.author,
        image_url=book.image_url,
        description=book.description,
        publication_info=book.publication_info,
        genres=book.genres,
        pages=book.pages,
        link=book.link,
        id=book.id
    )

    if db.query(models.Books).filter(models.Books.id == book.id).first():
        pass

    else:
        db.add(books_record)
        db.commit()

    library_record = models.Library(
        media_id=book.id,
        media_type="Book",
        username=user.username
    )

    if db.query(models.Library).filter(models.Library.username == user.username,
                                       models.Library.media_id == book.id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already added this book to Library")

    else:
        db.add(library_record)
        db.commit()

    return {"detail": "OK, Successfully Added Book to Library"}


@app.post('/library_add_movie')
async def library_add_movie(movie: Movie_Detail, user: User = Depends(fetch_user)):

    movies_record = models.Movies(
        title=movie.title,
        release_date=movie.release_date,
        image_url=movie.image_url,
        genre=movie.genre,
        length=movie.length,
        description=movie.description,
        actors=movie.actors,
        director=movie.director,
        screenplay=movie.screenplay,
        link=movie.link,
        id=movie.id
    )

    if db.query(models.Movies).filter(models.Movies.id == movie.id).first():
        pass

    else:
        db.add(movies_record)
        db.commit()

        library_record = models.Library(
            media_id=movie.id,
            media_type="Movie",
            username=user.username
        )

    if db.query(models.Library).filter(models.Library.username == user.username,
                                       models.Library.media_id == movie.id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already added this movie to Library")

    else:
        db.add(library_record)
        db.commit()

    return {"detail": "OK, Successfully Added Movie to Library"}


@app.post('/library_add_game')
async def library_add_game(game: Game_Detail, user: User = Depends(fetch_user)):

    games_record = models.Games(
        title=game.title,
        image_url=game.image_url,
        description=game.description,
        release_date=game.release_date,
        developer=game.developer,
        publisher=game.publisher,
        genres=game.genres,
        link=game.link
    )

    if db.query(models.Games).filter(models.Games.link == game.link).first():
        pass

    else:
        db.add(games_record)
        db.commit()

    library_record = models.Library(
        media_id=game.link,
        media_type="Game",
        username=user.username
    )

    if db.query(models.Library).filter(
            models.Library.username == user.username,
            models.Library.media_id == game.link).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="User already added this game to Library")

    else:
        db.add(library_record)
        db.commit()

    return {"detail": "OK, Successfully Added Game to Library"}


@app.get('/wishlist_get_my_books')
async def wishlist_get_my_books(user: User = Depends(fetch_user)):
    try:
        records = db.query(models.Books).filter(
            # don't need explicit foreign key relations
            models.Books.id == models.Wishlist.media_id,
            # does adding more parameters reduce complexity? :Hmmm
            models.Wishlist.username == user.username,
            models.Wishlist.media_type == "Book").all()  # don't need this
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when retrieving user's wishlist books")

    return records


@app.get('/wishlist_get_my_movies')
async def wishlist_get_my_movies(user: User = Depends(fetch_user)):
    try:
        records = db.query(models.Movies).filter(
            models.Movies.id == models.Wishlist.media_id,
            models.Wishlist.username == user.username,
            models.Wishlist.media_type == "Movie").all()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when retrieving user's wishlist movies")

    return records


@app.get('/wishlist_get_my_games')
async def wishlist_get_my_games(user: User = Depends(fetch_user)):
    try:
        records = db.query(models.Games).filter(
            models.Games.link == models.Wishlist.media_id,
            models.Wishlist.username == user.username,
            models.Wishlist.media_type == "Game").all()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when retrieving user's wishlist movies")

    return records


@app.get('/library_get_my_books')
async def library_get_my_books(user: User = Depends(fetch_user)):
    try:
        records = db.query(models.Books).filter(
            models.Books.id == models.Library.media_id,
            models.Library.username == user.username,
            models.Library.media_type == "Book").all()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when retrieving all library books")

    return records


@app.get('/library_get_my_movies')
async def library_get_my_movies(user: User = Depends(fetch_user)):
    try:
        records = db.query(models.Movies).filter(
            models.Movies.id == models.Library.media_id,
            models.Library.username == user.username,
            models.Library.media_type == "Movie").all()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when retrieving all library books")

    return records


@app.get('/library_get_my_games')
async def library_get_my_games(user: User = Depends(fetch_user)):
    try:
        records = db.query(models.Games).filter(
            models.Games.link == models.Library.media_id,
            models.Library.username == user.username,
            models.Library.media_type == "Game").all()
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when retrieving all library books")

    return records


@app.post('/delete_wishlist_item')
async def delete_wishlist_item(item_id: str, user: User = Depends(fetch_user)):
    try:
        db.query(models.Wishlist).filter(models.Wishlist.media_id == item_id,
                                         models.Wishlist.username == user.username,).delete()
        db.commit()

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when deleting wishlist item")

    return {"detail": "OK, Successfully Deleted Wishlist Item"}


@app.post('/delete_library_item')
async def delete_library_item(item_id: str, user: User = Depends(fetch_user)):
    try:
        db.query(models.Library).filter(models.Library.media_id == item_id,
                                        models.Library.username == user.username,).delete()
        db.commit()

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when deleting library item")

    return {"detail": "OK, Successfully Deleted Library Item"}


@app.post('/move_item_wishlist_to_library')
async def move_wishlist_library(item_id: str, user: User = Depends(fetch_user)):

    if db.query(models.Library).filter(models.Library.media_id == item_id, models.Library.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Item already exists in Library")

    try:

        record: Wishlist = db.query(models.Wishlist).filter(models.Wishlist.media_id == item_id,
                                                            models.Wishlist.username == user.username).first()

        library_record = models.Library(
            media_id=record.media_id,
            media_type=record.media_type,
            username=record.username
        )

        db.add(library_record)
        db.commit()

        await delete_wishlist_item(item_id, user)

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when moving wishlist item to library")

    return {"detail": "OK, Successfully Moved Wishlist Item to Library"}


@app.post('/move_item_library_to_wishlist')
async def move_library_wishlist(item_id: str, user: User = Depends(fetch_user)):

    if db.query(models.Wishlist).filter(models.Wishlist.media_id == item_id, models.Wishlist.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Item already exists in Wishlist")

    try:
        record: Library = db.query(models.Library).filter(models.Library.media_id == item_id,
                                                          models.Library.username == user.username).first()

        wishlist_record = models.Wishlist(
            media_id=record.media_id,
            media_type=record.media_type,
            username=record.username
        )

        db.add(wishlist_record)
        db.commit()

        await delete_library_item(item_id, user)

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when moving library item to wishlist")

    return {"detail": "OK, Successfully Moved Library Item to Wishlist"}


# Progress Endpoints

@app.post('/update_progress_books')
async def update_progress_books(progress_books_record: Progress_Books,  user: User = Depends(fetch_user)):

    try:
        record: Progress_Books = db.query(models.Progress_Books).filter(
            models.Progress_Books.media_id == progress_books_record.media_id, models.Progress_Books.username == user.username).first()

        if record:
            if progress_books_record.media_id:  # find better way
                record.media_id = progress_books_record.media_id
            if progress_books_record.hours_read:
                record.hours_read = progress_books_record.hours_read
            if progress_books_record.rating:
                record.rating = progress_books_record.rating
            if progress_books_record.notes:
                record.notes = progress_books_record.notes
            if progress_books_record.pages_read:
                record.pages_read = progress_books_record.pages_read

            record.username = user.username
            db.commit()

            return db.query(models.Progress_Books).filter(  # ideally would serialize to json
                models.Progress_Books.media_id == progress_books_record.media_id, models.Progress_Books.username == user.username).first()

        else:
            insert_record = models.Progress_Books(
                media_id=progress_books_record.media_id,
                hours_read="0",
                rating="Unrated",
                notes="",
                pages_read="0",
                username=user.username
            )

            db.add(insert_record)
            db.commit()

            return db.query(models.Progress_Books).filter(  # ideally would serialize to json
                models.Progress_Books.media_id == progress_books_record.media_id, models.Progress_Books.username == user.username).first()

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when moving updating Progress_Books table")


@app.post('/update_progress_games')
async def update_progress_games(progress_games_record: Progress_Games,  user: User = Depends(fetch_user)):

    try:
        record: Progress_Games = db.query(models.Progress_Games).filter(
            models.Progress_Games.media_id == progress_games_record.media_id, models.Progress_Games.username == user.username).first()

        if record:
            if progress_games_record.media_id:
                record.media_id = progress_games_record.media_id
            if progress_games_record.hours_played:
                record.hours_played = progress_games_record.hours_played
            if progress_games_record.rating:
                record.rating = progress_games_record.rating
            if progress_games_record.notes:
                record.notes = progress_games_record.notes

            record.username = user.username
            db.commit()

            return db.query(models.Progress_Games).filter(  # ideally would serialize to json
                models.Progress_Games.media_id == progress_games_record.media_id, models.Progress_Games.username == user.username).first()

        else:
            insert_record = models.Progress_Games(
                media_id=progress_games_record.media_id,
                hours_played="0",
                rating="Unrated",
                notes="",
                username=user.username
            )

            db.add(insert_record)
            db.commit()

            return db.query(models.Progress_Games).filter(  # ideally would serialize to json
                models.Progress_Games.media_id == progress_games_record.media_id, models.Progress_Games.username == user.username).first()

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when moving updating Progress_Games table")


@app.post('/update_progress_movies')
async def update_progress_movies(progress_movies_record: Progress_Movies,  user: User = Depends(fetch_user)):

    try:
        record: Progress_Movies = db.query(models.Progress_Movies).filter(
            models.Progress_Movies.media_id == progress_movies_record.media_id, models.Progress_Movies.username == user.username).first()

        if record:
            if progress_movies_record.media_id:
                record.media_id = progress_movies_record.media_id
            if progress_movies_record.hours_watched:
                record.hours_watched = progress_movies_record.hours_watched
            if progress_movies_record.rating:
                record.rating = progress_movies_record.rating
            if progress_movies_record.notes:
                record.notes = progress_movies_record.notes

            record.username = user.username
            db.commit()

            return db.query(models.Progress_Movies).filter(  # ideally would serialize to json
                models.Progress_Movies.media_id == progress_movies_record.media_id, models.Progress_Movies.username == user.username).first()

        else:
            insert_record = models.Progress_Movies(
                media_id=progress_movies_record.media_id,
                hours_watched="0",
                rating="Unrated",
                notes="",
                username=user.username
            )

            db.add(insert_record)
            db.commit()

            return db.query(models.Progress_Movies).filter(  # ideally would serialize to json
                models.Progress_Movies.media_id == progress_movies_record.media_id, models.Progress_Movies.username == user.username).first()

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when moving updating Progress_Movies table")
