from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from deps import get_current_user_id
from sqlalchemy import text

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ GET ACCOUNT INFO
@router.get("/")
def get_account(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("SELECT email FROM users WHERE id=:id"),
        {"id": user_id}
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return {"email": result[0]}

# ✅ UPDATE EMAIL
@router.post("/update")
def update_account(
    email: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db.execute(
        text("UPDATE users SET email=:email WHERE id=:id"),
        {"email": email, "id": user_id}
    )
    db.commit()

    return {"status": "updated"}