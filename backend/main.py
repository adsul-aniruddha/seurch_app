from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from search.ai_search import router as ai_router
from history.api import router as history_router
from settings.api import router as settings_router
from account.api import router as account_router
from web_creator.web_creator import router as web_creator_router
from app_creator.app_creator import router as app_creator_router
from logogenerator.logo_generator import router as logo_router

import sqlite3
import os

# ================= APP =================
app = FastAPI(title="All In One SaaS Backend 🚀")

# 🔥 AUTO CREATE FOLDERS
os.makedirs("generated_sites", exist_ok=True)
os.makedirs("generated_apps", exist_ok=True)
os.makedirs("generated_logos", exist_ok=True)

app.mount("/generated_sites", StaticFiles(directory="generated_sites"), name="sites")

# ================= ROUTERS =================
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(history_router, prefix="/history", tags=["History"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(account_router, prefix="/account", tags=["Account"])
app.include_router(web_creator_router, tags=["Web Creator"])
app.include_router(app_creator_router, tags=["App Creator"])
app.include_router(logo_router, tags=["Logo Generator"])

# ================= CORS (Frontend साठी) =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seurch-app.vercel.app",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CONFIG =================
SECRET_KEY = "seurch_app_secret_2024_change_this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 Week
DB_NAME = "app.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ================= DB =================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Auto create tables
with get_db() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        query TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

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
    return {"status": "ok", "backend": "https://seurch-app.onrender.com"}

# ================= SIGNUP =================
@app.post("/signup")
def signup(data: SignupData):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=?", (data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="User already exists")

        cur.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (data.email, hash_password(data.password))
        )
        conn.commit()
        return {"status": "created", "message": "Account created successfully"}
    finally:
        conn.close()

# ================= LOGIN =================
@app.post("/login")
def login(data: LoginData):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE email=?", (data.email,))
        row = cur.fetchone()
        
        if not row or not verify_password(data.password, row[1]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"user_id": row[0], "email": data.email})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        conn.close()

# 🔥 AUTO LOGIN TOKEN VERIFY
@app.get("/verify-token")
def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid/Expired token")

# ================= HISTORY =================
@app.post("/save-search")
def save_search(data: SearchData):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO search_history (email, query) VALUES (?, ?)",
            (data.email.strip(), data.query.strip())
        )
        conn.commit()
        return {"status": "saved"}
    finally:
        conn.close()

@app.get("/history")
def get_history(email: str):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT query, created_at FROM search_history WHERE email=? ORDER BY created_at DESC LIMIT 50", 
            (email,)
        )
        history = [{"query": row[0], "timestamp": row[1]} for row in cur.fetchall()]
        return history
    finally:
        conn.close()

# ================= SEARCH =================
@app.get("/search")
def search(q: str):
    return {
        "query": q,
        "results": [
            {
                "title": f"🔍 Top result for '{q}'",
                "url": f"https://www.google.com/search?q={q}",
                "thumbnail": "https://via.placeholder.com/320x180/667eea/ffffff?text=Search"
            }
        ]
    }

# ================= WEBSITE CREATOR =================
@app.post("/create-website")
def create_website(data: dict):
    name = data.get("name", "My Website")
    return {
        "name": name,
        "url": f"https://{name.lower().replace(' ', '-')}.webcreator.app",
        "html": f"<h1>{name}</h1><p>Generated by WebSearch Pro</p>",
        "preview": "https://via.placeholder.com/1200x600/203a43/ffffff?text=Website+Ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)