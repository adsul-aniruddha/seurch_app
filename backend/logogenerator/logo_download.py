import uuid
import os
from fastapi.responses import FileResponse

SAVE_PATH = "generated_logos"
os.makedirs(SAVE_PATH, exist_ok=True)

def save_logo(svg):
    file_id = str(uuid.uuid4())
    path = f"{SAVE_PATH}/{file_id}.svg"

    with open(path, "w") as f:
        f.write(svg)

    return file_id

def get_logo_file(file_id):
    path = f"{SAVE_PATH}/{file_id}.svg"
    return FileResponse(path)