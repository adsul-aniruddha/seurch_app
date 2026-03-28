from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from settings.models import Settings
from deps import get_current_user_id

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ GET SETTINGS
@router.get("/")
def get_settings(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    setting = db.query(Settings).filter(Settings.user_id == user_id).first()

    if not setting:
        setting = Settings(user_id=user_id, theme="dark")
        db.add(setting)
        db.commit()
        db.refresh(setting)

    return setting

# ✅ UPDATE SETTINGS
@router.post("/")
def update_settings(
    theme: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    setting = db.query(Settings).filter(Settings.user_id == user_id).first()

    if not setting:
        setting = Settings(user_id=user_id, theme=theme)
        db.add(setting)
    else:
        setting.theme = theme

    db.commit()

    return {"status": "updated"}