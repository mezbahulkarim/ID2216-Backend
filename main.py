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

@app.post('/search_activity')
async def activity_search(media_type:str, search: str, user: User = Depends(fetch_user)):
    
    try:
        if media_type == 'book':
            return search_book(search)

        if media_type == 'movie':
            return search_movie(search)

        if media_type == 'game':
            return search_game(search)

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="FAIL, error searching for activity")


def base64_toString(input: str):
    bytes= base64.urlsafe_b64decode(input)
    decoded_slash = bytes.decode("utf-8")
    decoded = decoded_slash.replace('SLASH', '/')       #scrapers line 13
    return decoded

async def check_in_wishlist_or_library(media_id:str, user: User = Depends(fetch_user)):
    if db.query(models.Library).filter(models.Library.media_id == media_id, models.Library.username == user.username).first():
        return 'library'

    if db.query(models.Wishlist).filter(models.Wishlist.media_id == media_id, models.Wishlist.username == user.username).first():
        return 'wishlist'

    return ''

async def check_progress_table(media_id:str, media_type:str, user: User = Depends(fetch_user)):
    
    if media_type == 'book':
        record = db.query(models.Progress_Books).filter(models.Progress_Books.media_id == media_id, models.Progress_Books.username == user.username).first()
        if record:
            return record

    if media_type == 'movie':
        record = db.query(models.Progress_Movies).filter(models.Progress_Movies.media_id == media_id, models.Progress_Movies.username == user.username).first()
        if record:
            return record
    
    if media_type == 'game':
        record = db.query(models.Progress_Games).filter(models.Progress_Games.media_id == media_id, models.Progress_Games.username == user.username).first()
        if record:
            return record
    
    return None

@app.post('/detail_activity')
async def activity_detail(media_type:str, encoded_link: str, user: User = Depends(fetch_user)):
    decoded = base64_toString(encoded_link)

    # try:
    if media_type == 'movie':
        coroutine = asyncio.create_task(detail_movie(decoded))
        await coroutine
        detail = coroutine.result()
        added_to = await check_in_wishlist_or_library(detail['id'], user)
        detail['added_to'] = added_to
        progress_record = await check_progress_table(detail['id'], 'movie', user)
        if progress_record:
            detail['hours_watched'] = progress_record.hours_watched
            detail['rating'] = progress_record.rating
            detail['notes'] = progress_record.notes
        return detail

    if media_type == 'book':
        detail = detail_book(decoded)
        added_to = await check_in_wishlist_or_library(detail['id'], user)
        detail['added_to'] = added_to
        progress_record = await check_progress_table(detail['id'], 'book', user)
        if progress_record:
            detail['hours_read'] = progress_record.hours_read
            detail['rating'] = progress_record.rating
            detail['notes'] = progress_record.notes
            detail['pages_read'] = progress_record.pages_read
        return detail

    if media_type == 'game':
        detail = detail_game(decoded)
        added_to = await check_in_wishlist_or_library(detail['link'], user)
        detail['added_to'] = added_to
        progress_record = await check_progress_table(detail['link'], 'game', user)
        if progress_record:
            detail['hours_played'] = progress_record.hours_played
            detail['rating'] = progress_record.rating
            detail['notes'] = progress_record.notes
        return detail
    # except:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail="FAIL, error searching for details of activity")


@app.post('/add_activity')
async def add_activity(media_type: str, encoded_link: str, wishlist_or_library: str, user: User = Depends(fetch_user)):
    try:
        table = ''
        add_to_progress: bool

        if wishlist_or_library == 'wishlist':
            table = models.Wishlist
            
        if wishlist_or_library == 'library':
            table = models.Library
            add_to_progress = True
        
        if media_type == 'book':
            book = await activity_detail(media_type, encoded_link, user)

            books_record = models.Books(
            title=book['title'],
            author=book['author'],
            image_url=book['image_url'],
            description=book['description'],
            publication_info=book['publication_info'],
            genres=book['genres'],
            pages=book['pages'],
            link=book['link'],
            link_encoded=book['link_encoded'],
            id=book['id']
            )

            if db.query(models.Books).filter(models.Books.id == book['id']).first():
                pass

            else:
                db.add(books_record)
                db.commit()

            table_record = table(
                media_id=book['id'],
                media_type="Book",
                username=user.username
            )

            if db.query(table).filter(table.username == user.username,
                                            table.media_id == book['id']).first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User already added this book to Wishlist or Library")

            else:
                db.add(table_record)
                db.commit()

            if add_to_progress:
                progress_record = models.Progress_Books(
                    media_id = book['id']
                )
                await update_progress_books(progress_record, user)    

        if media_type == 'movie':
            movie = await activity_detail(media_type, encoded_link, user)

            movies_record = models.Movies(
            title=movie['title'],
            release_date=movie['release_date'],
            image_url=movie['image_url'],
            genre=movie['genre'],
            length=movie['length'],
            description=movie['description'],
            actors=movie['actors'],
            director=movie['director'],
            screenplay=movie['screenplay'],
            link=movie['link'],
            link_encoded= movie['link_encoded'],
            id=movie['id']
            )

            if db.query(models.Movies).filter(models.Movies.id == movie['id']).first():
                pass

            else:
                db.add(movies_record)
                db.commit()

            table_record = table(
                media_id=movie['id'],
                media_type="Movie",
                username=user.username
            )

            if db.query(table).filter(table.username == user.username,
                                                table.media_id == movie['id']).first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="User already added this movie to Wishlist or Library")

            else:
                db.add(table_record)
                db.commit()

            if add_to_progress:
                progress_record = models.Progress_Movies(
                    media_id = movie['id']
                )
                await update_progress_movies(progress_record, user)    


        if media_type == 'game':
            game = await activity_detail(media_type, encoded_link, user)
            
            games_record = models.Games(
            title=game['title'],
            image_url=game['image_url'],
            description=game['description'],
            release_date=game['release_date'],
            developer=game['developer'],
            publisher=game['publisher'],
            genres=game['genres'],
            link=game['link'],
            link_encoded=game['link_encoded']
            )

            if db.query(models.Games).filter(models.Games.link == game['link']).first():
                pass

            else:
                db.add(games_record)
                db.commit()

            table_record = table(
                media_id=game['link'],
                media_type="Game",
                username=user.username
            )

            if db.query(table).filter(
                    table.username == user.username,
                    table.media_id == game['link']).first():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="User already added this game to Wishlist or Library")

            else:
                db.add(table_record)
                db.commit()

            if add_to_progress:
                progress_record = models.Progress_Games(
                    media_id = game['link']
                )
                await update_progress_games(progress_record, user)  


        return {"detail": "OK, Successfully Added Activity to Wishlist or Library"}
    
    except: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Error when adding activity to Wishlist or Library")


@app.get('/get_all_library_or_wishlist_items')
async def get_all_library_or_wishlist_items(wishlist_or_library: str, user: User = Depends(fetch_user)):
    
    table = ''
    
    if wishlist_or_library == 'wishlist':
        table = models.Wishlist

    if wishlist_or_library == 'library':
        table = models.Library

    book_records = db.query(models.Books).filter(
        table.username == user.username, models.Books.id == table.media_id).all()

    movie_records = db.query(models.Movies).filter(
        table.username == user.username, models.Movies.id == table.media_id).all()

    game_records = db.query(models.Games).filter(
        table.username == user.username, models.Games.link == table.media_id).all()
    
    return book_records + movie_records + game_records


@app.post('/delete_wishlist_or_library_item')
async def delete_item(wishlist_or_library:str ,item_id: str, user: User = Depends(fetch_user)):
    table = ''
    try:
        if wishlist_or_library == 'library':
            table = models.Library

        if wishlist_or_library == 'wishlist':
            table = models.Wishlist
    
        db.query(table).filter(table.media_id == item_id,
                                       table.username == user.username,).delete()
        db.commit()

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when deleting wishlist or library item")

    return {"detail": "OK, Successfully Deleted Wishlist or Library Item"}


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

        await delete_item('Wishlist',item_id, user)

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

        await delete_item('Library', item_id, user)

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
                rating="0",
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
                rating="0",
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
                rating="0",
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


#Get Attributes from Progress Table Endpoints
@app.get('/hours_spent')
def hours_spent(user: User = Depends(fetch_user)):
    try:
        hours_read =0
        hours_played =0
        hours_watched =0

        for record in db.query(models.Progress_Books).filter(models.Progress_Books.username == user.username):
            hours_read += float(record.hours_read)


        for record in db.query(models.Progress_Games).filter(models.Progress_Games.username == user.username):
            hours_played += float(record.hours_played)

        
        for record in db.query(models.Progress_Movies).filter(models.Progress_Movies.username == user.username):
            hours_watched += float(record.hours_watched)

        total_hours = str(hours_watched + hours_played + hours_read)

        hours_read = str(hours_read)
        hours_played = str(hours_played)
        hours_watched = str(hours_watched) 

        return {"hours_read": hours_read, "hours_played": hours_played, "hours_watched": hours_watched, "total_hours": total_hours}
    
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error when fetching hours spent for user")


@app.get('/ratings')
def ratings(user: User = Depends(fetch_user)):
    try:
        rating_books =0
        rating_games =0
        rating_movies =0
       
        i =0
        for record in db.query(models.Progress_Books).filter(models.Progress_Books.username == user.username):
            rating_books += float(record.rating)
            i=i+1
        rating_books = float(rating_books/i)
        rating_books = float(format(rating_books, '.2f'))

        j =0
        for record in db.query(models.Progress_Games).filter(models.Progress_Games.username == user.username):
            rating_games += float(record.rating)
            j=j+1
        rating_games =+ float(rating_games/j) #format(math.pi, '.2f')
        rating_games = float(format(rating_games, '.2f'))
        
        k=0
        for record in db.query(models.Progress_Movies).filter(models.Progress_Movies.username == user.username):
            rating_movies += float(record.rating)
            k=k+1
        rating_movies = float(rating_movies/k)
        rating_movies = float(format(rating_movies, '.2f'))

        total_ratings = float((rating_movies + rating_games + rating_books)/3)
        total_ratings = format(total_ratings, '.2f')

        rating_books = str(rating_books)
        rating_games = str(rating_games)
        rating_movies = str(rating_movies) 

        return {"rating_books": rating_books, "rating_games": rating_games, "rating_movies": rating_movies, "total_ratings": total_ratings}
    
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Error when fetching ratings for user")