from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from deps import get_current_user_id

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dummy discovery data (later real news/video API)
TRENDING = [
    {"type": "topic", "title": "Artificial Intelligence"},
    {"type": "topic", "title": "Cyber Security"},
    {"type": "video", "title": "Python Full Course"},
    {"type": "news", "title": "Tech layoffs slow down in 2026"},
    {"type": "topic", "title": "Data Science"},
]

@router.get("/discover")
def discovery_feed(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Later: personalize using interest table
    return {
        "user_id": user_id,
        "feed": TRENDING
    }

