from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter()

class AppRequest(BaseModel):
    app_name: str
    description: str


@router.post("/create-app")
def create_app(data: AppRequest):
    folder = f"generated_apps/{data.app_name.lower().replace(' ', '')}"

    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, "main.dart")

    dart_code = f"""
import 'package:flutter/material.dart';

void main() {{
  runApp(MyApp());
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text("{data.app_name}")),
        body: Center(
          child: Text("{data.description}"),
        ),
      ),
    );
  }}
}}
"""

    with open(file_path, "w") as f:
        f.write(dart_code)

    return {
        "message": "App created",
        "path": file_path
    }