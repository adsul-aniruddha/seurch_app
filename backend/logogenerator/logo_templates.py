from fastapi import APIRouter
import requests

router = APIRouter()

# 🔑 STEP 1: API KEY ITHE TAK
UNSPLASH_KEY = "pIucFKivGFhwlu1NHeGlnFr-HGhKpKnA50Vc9aGNRyY"


@router.get("/logo/templates")
def get_templates(query: str = "logo"):
    
    url = "https://api.unsplash.com/search/photos"
    
    params = {
        "query": query,
        "per_page": 20,
        "client_id": "pIucFKivGFhwlu1NHeGlnFr-HGhKpKnA50Vc9aGNRyY"   # 🔥 KEY USE HOTAY
    }

    response = requests.get(url, params=params)
    data = response.json()

    templates = []

    for item in data.get("results", []):
        templates.append({
            "id": item["id"],
            "name": item.get("alt_description") or "Logo",
            "image": item["urls"]["small"]
        })

    return templates