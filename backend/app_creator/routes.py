from fastapi import APIRouter
from typing import Dict, Any
from .generator import FlutterAppGenerator

router = APIRouter()

generator = FlutterAppGenerator()

@router.post("/create-app")
def create_app(data: Dict[str, Any]):
    return generator.create_flutter_app(data)