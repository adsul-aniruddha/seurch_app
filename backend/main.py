from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from search.ai_search import router as ai_router
from history.api import router as history_router
from settings.api import router as settings_router
from account.api import router as account_router
from web_creator.web_creator import router as web_creator_router

# 🔥 NEW IMPORTS
from app_creator.app_creator import router as app_creator_router
from logogenerator.logo_generator import router as logo_router

import sqlite3
import os

# ================= APP =================
app = FastAPI(title="All In One SaaS Backend 🚀")

# 🔥 AUTO CREATE FOLDERS
if not os.path.exists("generated_sites"):
    os.makedirs("generated_sites")

if not os.path.exists("generated_apps"):
    os.makedirs("generated_apps")

if not os.path.exists("generated_logos"):
    os.makedirs("generated_logos")

# 🔥 STATIC SERVE
app.mount("/generated_sites", StaticFiles(directory="generated_sites"), name="sites")

# ================= ROUTERS =================
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(history_router, prefix="/history", tags=["History"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(account_router, prefix="/account", tags=["Account"])
app.include_router(web_creator_router, tags=["Web Creator"])
app.include_router(app_creator_router, tags=["App Creator"])   # 🔥 NEW
app.include_router(logo_router, tags=["Logo Generator"])       # 🔥 NEW

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CONFIG =================
SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DB_NAME = "app.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ================= DB =================
def get_db():
    return sqlite3.connect(DB_NAME)

conn = get_db()

conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    query TEXT,
    created_at TEXT
)
""")

conn.close()

# ================= AUTH UTILS =================
def hash_password(password: str):
    return pwd_context.hash(password[:72])

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password[:72], hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ================= MODELS =================
class SignupData(BaseModel):
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

class SearchData(BaseModel):
    email: str
    query: str

# ================= ROOT =================
@app.get("/")
def root():
    return {"status": "ok", "message": "All-in-One SaaS Backend running 🚀"}

# ================= SIGNUP =================
@app.post("/signup")
def signup(data: SignupData):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=?", (data.email,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")

    cur.execute(
        "INSERT INTO users (email, password) VALUES (?, ?)",
        (data.email, hash_password(data.password))
    )

    conn.commit()
    conn.close()

    return {"status": "created"}

# ================= LOGIN =================
@app.post("/login")
def login(data: LoginData):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, password FROM users WHERE email=?", (data.email,))
    row = cur.fetchone()
    conn.close()

    if not row or not verify_password(data.password, row[1]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": row[0]})

    return {"access_token": token, "token_type": "bearer"}

# ================= SAVE SEARCH =================
@app.post("/save-search")
def save_search(data: SearchData):
    conn = get_db()

    conn.execute(
        "INSERT INTO search_history (email, query, created_at) VALUES (?, ?, ?)",
        (data.email.strip(), data.query.strip(), datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

    return {"status": "saved"}

# ================= SEARCH =================
@app.get("/search")
def search(q: str):
    return {
        "query": q,
        "results": [],
        "message": "Search logic here"
    }