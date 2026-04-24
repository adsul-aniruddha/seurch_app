from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import zipfile
from pathlib import Path

app = FastAPI(title="App Creator API 🚀")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= MODEL =================
class AppRequest(BaseModel):
    app_name: str

BASE_PATH = "generated_apps"

# ================= MAIN ROUTE =================
@app.post("/create-app")
def create_app(data: AppRequest):

    app_name = "".join(c for c in data.app_name if c.isalnum() or c == "_").lower()
    app_path = Path(BASE_PATH) / app_name

    # delete old app
    if app_path.exists():
        shutil.rmtree(app_path)

    # create folders
    (app_path / "lib").mkdir(parents=True, exist_ok=True)

    # ================= main.dart =================
    main_code = f"""
import 'package:flutter/material.dart';

void main() {{
  runApp(MyApp());
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        appBar: AppBar(title: Text("{app_name}")),
        body: Center(
          child: Text("🚀 {app_name} Created Successfully"),
        ),
      ),
    );
  }}
}}
"""
    with open(app_path / "lib/main.dart", "w") as f:
        f.write(main_code)

    # ================= pubspec.yaml =================
    pubspec = f"""
name: {app_name}
description: Generated App

environment:
  sdk: ">=3.0.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
"""
    with open(app_path / "pubspec.yaml", "w") as f:
        f.write(pubspec)

    # ================= ZIP =================
    zip_path = Path(BASE_PATH) / f"{app_name}.zip"

    with zipfile.ZipFile(zip_path, 'w') as z:
        for root, dirs, files in os.walk(app_path):
            for file in files:
                full_path = Path(root) / file
                z.write(full_path, full_path.relative_to(app_path))

    return {
        "success": True,
        "app_name": app_name,
        "folder": str(app_path),
        "zip": str(zip_path)
    }

# ================= ROOT =================
@app.get("/")
def home():
    return {"msg": "App Creator Running 🚀"}

# ================= RUN =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8081, reload=True)