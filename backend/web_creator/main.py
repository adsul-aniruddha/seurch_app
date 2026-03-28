from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# 🔥 import router
from web_creator import router as web_router

app = FastAPI(title="Web Creator Service 🚀")

# ✅ CORS (Flutter connect साठी)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 ensure folder exists
if not os.path.exists("generated_sites"):
    os.makedirs("generated_sites")

# 🔥 static serve
app.mount("/generated_sites", StaticFiles(directory="generated_sites"), name="sites")

# 🔥 router include
app.include_router(web_router)

# 🔥 test route
@app.get("/")
def root():
    return {"status": "Web Creator running ✅"}