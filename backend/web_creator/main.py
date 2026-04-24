from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 🔥 ONLY WEB ROUTER
from app_main import router as app_router

app = FastAPI(title="Web Creator 🚀")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= STATIC FILES =================
# 👉 generated website serve karayla
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

# ================= ROUTER =================
app.include_router(app_router, prefix="/app", tags=["Web Creator"])

# ================= ROOT =================
@app.get("/")
def root():
    return {
        "status": "Web Creator Running 🚀"
    }