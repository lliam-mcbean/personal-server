from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, ReturnDocument
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()
client = MongoClient("mongodb+srv://lliammcbean:yniSWTrzKrE41iNW@cluster0.ggq86fh.mongodb.net/")
db = client.personal

origins = ["http://localhost:3000", "https://lliam-test.netlify.app", "http://localhost:5173", "https://tomagotchi.netlify.app"]

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

@app.get('/tomagotchi/{user_id}')
def root(user_id: str):
    collection = db.tomagotchi
    current_time = time.time()

    tomagotchi = collection.find_one({"user": user_id})
    if not tomagotchi:
        raise HTTPException(status_code=404, detail="Tomagotchi not found")

    time_since_creation = current_time - tomagotchi["created_at"]
    time_since_last_fed = current_time - tomagotchi["last_fed"]

    if time_since_creation < 86400:
        evolution = 0
    elif 86400 <= time_since_creation < 86400 * 2:
        evolution = 1
    else:
        evolution = 2

    if time_since_last_fed > 172800:
        status = "dead"
    elif time_since_last_fed > 86400:
        status = "dying"
    elif time_since_last_fed > 28800:
        status = "hungry"
    else:
        status = "healthy"

    updated_tomagotchi = collection.find_one_and_update(
        {"user": user_id},
        {"$set": {"evolution": evolution, "status": status}},
        return_document=ReturnDocument.AFTER
    )

    updated_tomagotchi["_id"] = str(updated_tomagotchi["_id"])
    return updated_tomagotchi

@app.put('/tomagotchi/{user_id}')
def root(user_id: str):
    collection = db.tomagotchi
    currentTime = time.time()
    tomagotchi = collection.find_one_and_update({"user": user_id}, {'$set': {
        "last_fed": currentTime, 
        "created_at": currentTime, 
        "evolution": 0, 
        "status": "healthy"
        }}, return_document=ReturnDocument.AFTER)
    
    if not tomagotchi:
        return HTTPException(status_code=500, detail=f"An error occurred")
    
    tomagotchi["_id"] = str(tomagotchi["_id"])
    return tomagotchi

@app.put('/tomagotchi/{user_id}/{feed_time}')
def root(user_id: str, feed_time: float):
    collection = db.tomagotchi
    tomagotchi = collection.find_one({"user": user_id})

    if (tomagotchi["status"] != "dead"):
        tomagotchi = collection.find_one_and_update({"user": user_id}, {'$set': {
            "last_fed": feed_time, 
            "status": "healthy"
            }}, return_document=ReturnDocument.AFTER)

    if not tomagotchi:
        return HTTPException(status_code=500, detail=f"An error occurred")
    
    tomagotchi["_id"] = str(tomagotchi["_id"])
    return tomagotchi



@app.get('/user/{user_id}/{user_email}')
def root(user_id: str, user_email: str):
    collection = db.users
    tomagotchi = db.tomagotchi

    existing_user = collection.find_one({"user_id": user_id})

    if not existing_user:
        result = collection.insert_one({
                "user_id": user_id, 
                "email": user_email
            })
        tomagotchi.insert_one({
                "user": user_id,
                "created_at": time.time(),
                "last_fed": time.time(),
                "status": "healthy",
                "evolution": 0
            })
        existing_user = collection.find_one({"_id": result.inserted_id})
    
    existing_user["_id"] = str(existing_user["_id"])
    return existing_user

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