from fastapi import FastAPI, HTTPException, Header, Depends, APIRouter
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
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
DB_NAME = "app.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ================= DB =================
class Database:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

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

# ================= AUTH =================
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
        email = payload.get("email")
        if not email:
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
    return {"status": "ok"}

# ================= SIGNUP =================
@app.post("/signup")
def signup(data: SignupData):
    with Database() as db:
        db.cursor.execute("SELECT id FROM users WHERE email=?", (data.email,))
        if db.cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email exists")

        db.cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (data.email, hash_password(data.password))
        )
        return {"msg": "User created"}

# ================= LOGIN =================
@app.post("/login")
def login(data: LoginData):
    with Database() as db:
        db.cursor.execute("SELECT * FROM users WHERE email=?", (data.email,))
        user = db.cursor.fetchone()

        if not user or not verify_password(data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"email": user["email"]})
        return {"access_token": token, "token_type": "bearer"}

# ================= SEARCH =================
@app.get("/search")
def search(q: str):
    return {"query": q, "results": [f"Result for {q}"]}

# ================= HISTORY =================
@app.post("/save-search")
def save_search(data: SearchData, user=Depends(get_current_user)):
    with Database() as db:
        db.cursor.execute(
            "INSERT INTO search_history (email, query) VALUES (?, ?)",
            (user["email"], data.query)
        )
    return {"msg": "saved"}

@app.get("/history")
def get_history(user=Depends(get_current_user)):
    with Database() as db:
        db.cursor.execute(
            "SELECT * FROM search_history WHERE email=?",
            (user["email"],)
        )
        return [dict(row) for row in db.cursor.fetchall()]

# ================= ADMIN =================
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

def admin_only(user=Depends(get_current_user)):
    if user["email"] != "admin@gmail.com":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

@admin_router.get("/users")
def get_users(user=Depends(admin_only)):
    with Database() as db:
        db.cursor.execute("SELECT id, email, created_at FROM users")
        return [dict(row) for row in db.cursor.fetchall()]

@admin_router.get("/search-logs")
def get_logs(user=Depends(admin_only)):
    with Database() as db:
        db.cursor.execute("SELECT * FROM search_history")
        return [dict(row) for row in db.cursor.fetchall()]

@admin_router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, user=Depends(admin_only)):
    with Database() as db:
        db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    return {"msg": "user deleted"}

# 🔥 INCLUDE ADMIN ROUTER
app.include_router(admin_router)

# ================= RUN =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8081)