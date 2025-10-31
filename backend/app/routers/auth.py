# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User as DBUser
from app.schemas.user import UserCreate, UserOut 
from app.utils.security import create_access_token, verify_password, get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
def login(payload: UserCreate, db: Session = Depends(get_db)):
    """
    以 email/password 登入，成功回傳 Access Token。
    注意：UserCreate 若還包含 name 等欄位也沒關係，我們只取 email/password。
    """
    email = payload.email
    password = payload.password

    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    token = create_access_token(sub=str(user.id)) 
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: DBUser = Depends(get_current_user)):
    """
    取得目前登入者資訊（由 Bearer Token 決定）。
    """
    return current_user
