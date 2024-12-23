from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import json
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

users_db = {}

SECRET_KEY = "testidfhrtgdwref<@grsd85fesdx-tersgdgesrdvuyjt4twrsgdsfdgdgd"
ALGORITHM = "HS256"

class User(BaseModel):
    username: str
    password: str
    role: Optional[str] = "member"

class UserLogin(BaseModel):
    username: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return users_db.get(username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

@router.post("/register")
async def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    users_db[user.username] = {
        "username": user.username,
        "password": user.password,  # In production, hash the password!
        "role": user.role
    }
    return {"message": "User created successfully"}

@router.post("/login")
async def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=400, detail="User not found")
    stored_user = users_db[user.username]
    if stored_user["password"] != user.password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_token({"sub": user.username, "role": stored_user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return users_db