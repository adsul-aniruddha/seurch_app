from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from history.models import SearchHistory
from deps import get_current_user_id

# ✅ ROUTER DEFINE (हे missing होतं)
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/history")
def get_history(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return db.query(SearchHistory).filter(
        SearchHistory.user_id == user_id
    ).all()

@router.delete("/history/delete")
def delete_history(
    id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    item = db.query(SearchHistory).filter(
        SearchHistory.id == id,
        SearchHistory.user_id == user_id
    ).first()

    if item:
        db.delete(item)
        db.commit()

    return {"status": "deleted"}


