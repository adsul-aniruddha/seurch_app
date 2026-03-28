from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app_creator import router

app = FastAPI(title="App Creator 🚀")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "App Creator running"}