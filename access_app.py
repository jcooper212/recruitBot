from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import sqlite3

# Define a secret key (change this to a secure random value in production)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Connect to SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Function to generate JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to authenticate user
async def authenticate_user(username: str, password: str):
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if not user:
        return False
    return {"username": user[1], "role": user[2]}

# Function to ensure only owner can access
async def only_owner(user: dict = Depends(authenticate_user)):
    if not user or user["role"] != "Owner":
        raise HTTPException(status_code=403, detail="Only owner can perform this action")
    return user

# Route to authenticate user and generate JWT token
@app.post("/token")
async def login_for_access_token(username: str, password: str):
    authenticated_user = await authenticate_user(username, password)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(authenticated_user)
    return {"access_token": access_token, "token_type": "bearer"}

# Function to create users table
@app.get("/create_users_table")
async def create_users_table(user: dict = Depends(only_owner)):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    conn.commit()
    return {"message": "Users table created successfully"}

# Function to populate users table
@app.post("/populate_users_table")
async def populate_users_table(users: list):
    for user in users:
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', (user["username"], user["password"], user["role"]))
    conn.commit()
    return {"message": "Users table populated successfully"}

# # Function to create new DB
# @app.get("/create_db")
# async def createDB(user: dict = Depends(only_owner)):
#     # Your existing create_db logic here...
#     return {"message": "Database created successfully"}

# # Function to preload DB
# @app.get("/preload_db")
# async def preloadDB(user: dict = Depends(only_owner)):
#     # Your existing preload_db logic here...
#     return {"message": "Database preloaded successfully"}

# # Your existing routes...

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="127.0.0.1", port=8000)
