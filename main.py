from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import bcrypt
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# আপনার MongoDB Connection String
MONGO_URI = "mongodb+srv://mahimpatwary68_db_user:%40125mahim@cluster0.gxxosim.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["bmt_ai_db"]
users_collection = db["users"]

class User(BaseModel):
    name: str = None
    email: str
    password: str

@app.get("/")
def read_root():
    return {"status": "BMT AI Server is Running"}

@app.post("/signup")
async def signup(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists!")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }
    users_collection.insert_one(user_data)
    return {"message": "User created successfully"}

@app.post("/login")
async def login(user: User):
    db_user = users_collection.find_one({"email": user.email})
    if db_user and bcrypt.checkpw(user.password.encode('utf-8'), db_user["password"]):
        return {
            "status": "success",
            "name": db_user["name"],
            "email": db_user["email"]
        }
    raise HTTPException(status_code=401, detail="Invalid email or password")

if __name__ == "__main__":
    import uvicorn
    # Render-এর জন্য Port ডাইনামিক করা হয়েছে
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
