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
async def change_username(username: str, user:User = Depends(fetch_user)):      # WE NEED TO KICK THEM OUT/LOGOUT otherwise still logged in with previous username
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
async def change_email(email: str, user:User = Depends(fetch_user)):            # why can they log in with previous username, it still results in fail but sus
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

#Scraper Endpoints
@app.post('/search_movie')
async def movie_search(search: str, user:User= Depends(fetch_user)):
    try:
        return search_movie(search)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error searching for movie")


@app.post('/search_book')
async def book_search(search: str, user:User = Depends(fetch_user)):
    try:
        return search_book(search)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error searching for book")


@app.post('/search_game')
async def game_search(search: str, user:User = Depends(fetch_user)):
    try:
        return search_game(search)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error searching for game")


@app.post('/detail_movie', )
async def movie_detail(search: str, user:User = Depends(fetch_user)):
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
async def game_detail(search: str, user:User = Depends(fetch_user)):
    try:
        return_val = detail_game(search)
        # game: Game_Detail = return_val
        # return game
        return return_val
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error getting game details")
    #NOTES for game_detail- randomly getting this error sometimes, POSSIBLY FOR 18+ GAMES:
    # title = page_soup.find('div', class_="apphub_AppName").text.strip()
    # AttributeError: 'NoneType' object has no attribute 'text'

@app.post('/detail_book')
async def book_detail(search: str, user:User = Depends(fetch_user)):
    try:
        return_val = detail_book(search)
        # book: Book_Detail = return_val
        # return book
        return return_val
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="FAIL, error getting book details")


