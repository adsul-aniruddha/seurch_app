from fastapi import APIRouter
import requests
from .assets import COLORS, FONTS, ICONS

router = APIRouter()

# 🔑 KEY
UNSPLASH_KEY = "pIucFKivGFhwlu1NHeGlnFr-HGhKpKnA50Vc9aGNRyY"

# 🔥 TEMPLATES
@router.get("/templates")
def get_templates(query: str = "logo"):
    url = "https://api.unsplash.com/search/photos"

    params = {
        "query": query,
        "per_page": 20,
        "client_id": "pIucFKivGFhwlu1NHeGlnFr-HGhKpKnA50Vc9aGNRyY"
    }

    res = requests.get(url, params=params)
    data = res.json()

    templates = []

    for item in data.get("results", []):
        templates.append({
            "id": item["id"],
            "name": item.get("alt_description") or "Logo",
            "image": item["urls"]["small"]
        })

    return templates


# 🔥 ASSETS
@router.get("/assets")
def get_assets():
    return {
        "colors": COLORS,
        "fonts": FONTS,
        "icons": ICONS
    }


# 🔥 MENU (FIXED INDENTATION)
@router.get("/menu")
def get_menu():
    return [
        {"title": "Logo Editor", "icon": "edit", "route": "editor"},
        {"title": "Templates", "icon": "image", "route": "templates"},
        {"title": "Color Studio", "icon": "palette", "route": "color"},
        {"title": "AI Generator", "icon": "smart_toy", "route": "ai"},
        {"title": "Typography", "icon": "text_fields", "route": "text"},
        {"title": "Layers Pro", "icon": "layers", "route": "layers"},
        {"title": "Animate Logo", "icon": "animation", "route": "animate"},
        {"title": "Vector Shapes", "icon": "category", "route": "shapes"},
        {"title": "Export All", "icon": "download", "route": "export"},
        {"title": "Trends", "icon": "trending_up", "route": "trends"},
        {"title": "My Logos", "icon": "favorite", "route": "mylogos"},
        {"title": "Cloud Sync", "icon": "cloud", "route": "cloud"}
    ]