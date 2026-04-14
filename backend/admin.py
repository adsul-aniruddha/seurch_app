from fastapi import APIRouter, Depends, HTTPException
from deps import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

# 🔐 Admin check
def admin_only(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

# 👨‍💼 All users
@router.get("/users")
def get_users(user=Depends(admin_only)):
    return {"msg": "All users visible to admin"}

# 📊 All search logs
@router.get("/search-logs")
def get_logs(user=Depends(admin_only)):
    return {"msg": "All searches visible to admin"}

# 🚫 Ban user
@router.post("/ban/{user_id}")
def ban_user(user_id: int, user=Depends(admin_only)):
    return {"msg": f"user {user_id} banned"}