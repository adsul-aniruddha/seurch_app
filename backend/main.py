from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

import sqlite3
import os

# ================= APP =================
app = FastAPI(title="All In One SaaS Backend 🚀")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CONFIG =================
SECRET_KEY = "seurch_app_secret_2024_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
DB_NAME = "app.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ================= DB CONTEXT MANAGER =================
class Database:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

# Auto create tables (wrapped in try-catch)
try:
    with Database() as db:
        db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            query TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
except Exception as e:
    print(f"DB init warning: {e}")

# ================= AUTH UTILS =================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ================= MODELS =================
class SignupData(BaseModel):
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

# ================= ROUTES =================
@app.get("/")
def root():
    return {"status": "ok", "backend": "running"}

@app.post("/signup")
def signup(data: SignupData):
    with Database() as db:
        db.cursor.execute("SELECT id FROM users WHERE email = ?", (data.email.lower().strip(),))
        if db.cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = hash_password(data.password)
        db.cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (data.email.lower().strip(), hashed_password)
        )
        return {"status": "created"}

@app.post("/login")
def login(data: LoginData):
    with Database() as db:
        db.cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (data.email.lower().strip(),))
        user = db.cursor.fetchone()
        
        if not user or not verify_password(data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token({"email": user["email"]})
        return {"access_token": token, "email": user["email"]}

@app.get("/verify-token")
def verify_token(current_user: dict = Depends(get_current_user)):
    return {"valid": True, "email": current_user["email"]}