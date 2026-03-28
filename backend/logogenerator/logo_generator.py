from fastapi import APIRouter
from pydantic import BaseModel
from PIL import Image, ImageDraw
import os

router = APIRouter()

class LogoRequest(BaseModel):
    name: str


@router.post("/create-logo")
def create_logo(data: LogoRequest):
    folder = "generated_logos"

    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, f"{data.name}.png")

    img = Image.new('RGB', (400, 200), color=(15, 32, 39))
    d = ImageDraw.Draw(img)
    d.text((50, 80), data.name, fill=(0, 255, 204))

    img.save(file_path)

    return {
        "message": "Logo created",
        "path": file_path
    }