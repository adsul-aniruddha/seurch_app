from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logogenerator.logo_main import router as logo_router

# 🔥 IMPORT ALL MODULES
from auth_api import router as auth_router
from app_main import router as app_router   # 👈 तुझा create-app file
from logo_main import router as logo_router

app = FastAPI(title="All-in-One SaaS Backend 🚀")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= INCLUDE ROUTERS =================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(app_router, prefix="/app", tags=["App Creator"])  # 👈 important
app.include_router(logo_router, prefix="/logo", tags=["Logo"])
app.include_router(logo_router, prefix="/logo", tags=["Logo"])

# ================= ROOT =================
@app.get("/")
def root():
    return {
        "status": "All services running 🚀",
        "modules": ["Auth", "App Creator", "Logo"]
    }