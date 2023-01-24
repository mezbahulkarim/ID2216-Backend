from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client
import os
from pydantic import BaseModel

class TestTableField(BaseModel):
    id: int
    Name: str

load_dotenv()
app = FastAPI()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase= create_client(url, key) 

@app.get("/")
def root():
    return "At root, no Path Specified"

@app.get("/fields")
def get_fields():
    fields = supabase.table('Test').select('id').like('Name', 'L').execute()
    fields = fields.json()
    #print(type(fields))
    return fields

@app.post("/send_data")
async def send_data(record: TestTableField):
    data = supabase.table('Test').insert({"Name":record.Name, "id":record.id}).execute()
    data = data.json()
    return data




