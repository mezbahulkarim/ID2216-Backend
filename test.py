from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from supabase import create_client
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt 

load_dotenv()
app = FastAPI()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
JWT_SECRET = "shhh"

supabase= create_client(url, key) 

class User(BaseModel):
    username: str
    password: str

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')



@app.post('/users')
async def create_user(User: User):

    user_entry = supabase.table('User').insert({"username":User.username, "password": User.password}).execute()
    return "User Created: "+ User.username



@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):

    user = supabase.table('User').select("*").like('username', form_data.username).like('password', form_data.password).execute()
    
    if not user.data:
        return {'error': 'invalid credentials'}

    #user_obj = User.parse_obj(user.data[0])    convert Dict to Pydantic Model
    token = jwt.encode(user.data[0], JWT_SECRET)            #maybe change this not including password 
    
    return {'access_token': token, 'token_type': 'bearer'}



async def get_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms = ['HS256'])
        user_obj = User.parse_obj(payload)

    except:
        return {'error': "Invalid Username or Password"}

    return user_obj

@app.get('/mytoken')
async def get_my_token(user: User = Depends(get_user)): #depend on get_user for all user auth endpoints 
    return user





