from fastapi import FastAPI, Path
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    Book:str
    Pages_Read: int

class UpdateItem(BaseModel):
    Book: Optional[str] = None
    Pages_Read: Optional[str] = None

# @app.get("/")
# def home():
#     return {"Data": "yowzers"}

# @app.get("/info")
# def info():
#     return {"Number": 1}

sample = {"1984":{"Book": "1984", "Pages_Read": 88, "Total Pages": 500, "Rating": 5}}
inventory = {1:{"Book": "1984", "Pages_Read": 88}}

#Path can check input ge, gt fields
#Path parameters
@app.get("/get-book/{book_name}")
def get_book(book_name: str = Path(None, description="Name of the Book")):
    return sample[book_name]

#Query Parameters
@app.get("/get-from-key")
def get_value(pages:int ,name: Optional[str] =None):
    for i in sample:
        if sample[i]["Book"] == name:
            return sample[i]
    return "No Data Found"


@app.post("/create-item/{item_id}")
def create_item(item_id: int, item: Item):
    if item_id in inventory:
        return {"Item exists already"}

    inventory[item_id] = {"Book": item.Book, "Pages_Read": item.Pages_Read}
    return inventory[item_id]

@app.put("/update/{item_id}")
def update_item(item_id: int, item: UpdateItem):
    if item_id not in inventory:
        return {"Error ITEM EXISTS"}

    if item.Book!= None:
        inventory[item_id]["Book"] = item.Book

    if item.Pages_Read!= None:
        inventory[item_id]["Pages_Read"] = item.Book

    return inventory

@app.delete("delete")
def delete(item_id: int):
    if item_id not in inventory:
        return {"ID not exist"}

    del inventory[item_id]
    return {"item deleted"}