from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from supabase import create_client
import os
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import create_client
import jwt 
from passlib.hash import bcrypt


load_dotenv()
app = FastAPI()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
JWT_SECRET = os.environ.get("JWT_SECRET")


supabase= create_client(url, key)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') 

class User(BaseModel):
    username: str
    password: str
    email: str

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
