from fastapi import FastAPI
from logo_main import router

app = FastAPI()
app.include_router(router, prefix="/logo")