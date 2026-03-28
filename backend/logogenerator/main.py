from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logo_generator import router

app = FastAPI(title="Logo Generator 🚀")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Logo Generator running"}