from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from search.indexer import MiniSearchEngine
from history.models import SearchHistory
from deps import get_current_user_id

# ✅ ROUTER DEFINE (हेच missing होतं)
router = APIRouter()

# search engine init
engine = MiniSearchEngine()
engine.build_index()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/search")
def search_api(
    q: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    h = SearchHistory(user_id=user_id, query=q)
    db.add(h)
    db.commit()

    results = engine.search(q)
    return {
        "query": q,
        "results": results
    }

