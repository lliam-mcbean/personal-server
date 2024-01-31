from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List

app = FastAPI()
client = MongoClient("mongodb+srv://lliammcbean:yniSWTrzKrE41iNW@cluster0.ggq86fh.mongodb.net/")
db = client.personal

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class drawings(BaseModel):
    data: List[List[float]]

class Drawing(BaseModel):
    data: List[List[float]]

@app.get("/drawings")
async def root():
    collection = db.drawings.find()
    drawings = []
    for doc in collection:
        drawings.insert(0, doc['coords'])
        
    return drawings

@app.post("/drawings")
async def root(drawing: Drawing):
    try: 
        db.drawings.insert_one({"coords": drawing.data})
        collection = db.drawings.find()
        drawings = []
        for doc in collection:
            drawings.insert(0, doc['coords'])
            
        return {"success": True, "data": drawings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")