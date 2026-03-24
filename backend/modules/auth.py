import sqlite3
import os
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "korhex-super-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "users.db")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_password_hash(password: str) -> str:
    salt = b"korhex_salt"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    preferences TEXT
                )''')
    try:
        c.execute("ALTER TABLE users ADD COLUMN preferences TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.commit()
    
    # Check if admin exists
    c.execute("SELECT id FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  ('admin', get_password_hash('admin123'), 'admin'))
        conn.commit()
    conn.close()

init_db()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    preferences: str | None = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    password: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, role FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user is None:
        raise credentials_exception
        
    return {"user": user[0], "role": user[1]}

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, password_hash, role, preferences FROM users WHERE username = ?", (form_data.username,))
    user = c.fetchone()
    conn.close()
    
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user[0], "role": user[2]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user[2], "username": user[0], "preferences": user[3]}

@router.get("/me/prefs")
async def get_my_prefs(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT preferences FROM users WHERE username = ?", (current_user["user"],))
    prefs = c.fetchone()[0]
    conn.close()
    return {"preferences": prefs}

@router.post("/me/prefs")
async def save_my_prefs(data: dict, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    prefs_json = data.get("preferences")
    c.execute("UPDATE users SET preferences = ? WHERE username = ?", (prefs_json, current_user["user"]))
    conn.commit()
    conn.close()
    return {"message": "Preferences saved"}

@router.get("/users")
async def get_users(current_admin: dict = Depends(get_current_admin)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return users

@router.post("/users")
async def create_user(user: UserCreate, current_admin: dict = Depends(get_current_admin)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  (user.username, get_password_hash(user.password), user.role))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    conn.close()
    return {"message": "User created successfully"}

@router.delete("/users/{username}")
async def delete_user(username: str, current_admin: dict = Depends(get_current_admin)):
    if username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete super admin")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return {"message": "User deleted"}

@router.put("/users/{username}/password")
async def update_password(username: str, update: UserUpdate, current_admin: dict = Depends(get_current_admin)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
              (get_password_hash(update.password), username))
    conn.commit()
    conn.close()
    return {"message": "Password updated"}
