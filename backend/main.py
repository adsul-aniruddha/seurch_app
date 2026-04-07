from fastapi import FastAPI, HTTPException, Header, Depends
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

# ================= CORS =================
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
SECRET_KEY = "seurch_app_secret_2024_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 Week
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

# Auto create tables
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

# ================= AUTH UTILS =================
def hash_password(password: str) -> str:
    """Hash password safely (bcrypt handles length limits)"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password safely"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: str = Header(None)):
    """Dependency to get current user from token"""
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
    with Database() as db:
        # Check if user exists
        db.cursor.execute("SELECT id FROM users WHERE email = ?", (data.email.lower().strip(),))
        if db.cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed_password = hash_password(data.password)
        db.cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (data.email.lower().strip(), hashed_password)
        )
        
        return {"status": "created", "message": "Account created successfully"}

# ================= LOGIN =================
@app.post("/login")
def login(data: LoginData):
    with Database() as db:
        # Find user
        db.cursor.execute(
            "SELECT id, email, password FROM users WHERE email = ?", 
            (data.email.lower().strip(),)
        )
        user = db.cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create token
        token = create_access_token({"user_id": user["id"], "email": user["email"]})
        return {"access_token": token, "token_type": "bearer", "email": user["email"]}

# ================= TOKEN VERIFY =================
@app.get("/verify-token")
def verify_token(current_user: dict = Depends(get_current_user)):
    return {"valid": True, "email": current_user["email"]}

# ================= HISTORY =================
@app.post("/save-search")
def save_search(data: SearchData, current_user: dict = Depends(get_current_user)):
    with Database() as db:
        db.cursor.execute(
            "INSERT INTO search_history (email, query) VALUES (?, ?)",
            (current_user["email"], data.query.strip())
        )
        return {"status": "saved"}

@app.get("/history")
def get_history(current_user: dict = Depends(get_current_user)):
    with Database() as db:
        db.cursor.execute(
            "SELECT query, created_at FROM search_history WHERE email=? ORDER BY created_at DESC LIMIT 50", 
            (current_user["email"],)
        )
        history = [{"query": row["query"], "timestamp": row["created_at"]} for row in db.cursor.fetchall()]
        return history

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
def create_website(data: dict, current_user: dict = Depends(get_current_user)):
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