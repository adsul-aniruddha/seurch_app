from fastapi import APIRouter
from pydantic import BaseModel
import requests

router = APIRouter()

class Query(BaseModel):
    question: str


@router.post("/ai-search")
def ai_search(data: Query):
    query = data.question

    # 🔥 Simple AI logic (free method)
    response = requests.get(
        f"https://api.duckduckgo.com/?q={query}&format=json"
    ).json()

    answer = response.get("AbstractText", "")

    if not answer:
        answer = "No AI answer found. Try different query."

    return {
        "question": query,
        "answer": answer
    }