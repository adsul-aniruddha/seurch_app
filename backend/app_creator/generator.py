import os
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any
from .templates import generate_main_dart, generate_pubspec
from .utils import sanitize_name

BASE_PATH = "generated_apps"

class FlutterAppGenerator:

    def __init__(self):
        os.makedirs(BASE_PATH, exist_ok=True)

    def create_flutter_app(self, data: Dict[str, Any]):
        app_name = sanitize_name(data.get("app_name", "my_app"))

        app_path = Path(BASE_PATH) / app_name

        # delete old
        if app_path.exists():
            shutil.rmtree(app_path)

        # create structure
        (app_path / "lib").mkdir(parents=True, exist_ok=True)

        # files
        generate_main_dart(app_path, app_name)
        generate_pubspec(app_path, app_name)

        # zip
        zip_path = self.create_zip(app_path, app_name)

        return {
            "success": True,
            "app_name": app_name,
            "zip": str(zip_path)
        }

    def create_zip(self, app_path: Path, app_name: str):
        zip_path = Path(BASE_PATH) / f"{app_name}.zip"

        with zipfile.ZipFile(zip_path, 'w') as z:
            for root, dirs, files in os.walk(app_path):
                for file in files:
                    full_path = Path(root) / file
                    z.write(full_path, full_path.relative_to(app_path))

        return zip_path