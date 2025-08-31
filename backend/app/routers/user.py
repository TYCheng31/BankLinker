from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.user import User as DBUser
from app.schemas.user import UserCreate, UserOut
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 檢查 email 是否已經存在
    db_user = db.query(DBUser).filter(DBUser.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 加密密碼
    hashed_password = hash_password(user.password)
    db_user = DBUser(email=user.email, password_hash=hashed_password)
    
    # 儲存用戶
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
