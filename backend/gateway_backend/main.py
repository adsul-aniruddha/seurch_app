from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔥 direct import routers
from web_creator.web_creator import router as web_router
from app_creator.app_creator import router as app_router
from logogenerator.logo_generator import router as logo_router

app = FastAPI(title="All-in-One SaaS API 🚀")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 include all modules
app.include_router(web_router)
app.include_router(app_router)
app.include_router(logo_router)

@app.get("/")
def root():
    return {"status": "All services running via gateway 🚀"}