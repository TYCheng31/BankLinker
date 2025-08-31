# app/schemas/bank_connection.py
from pydantic import BaseModel
from datetime import datetime

class BankConnectionCreate(BaseModel):
    provider: str        # 讓 DB 來驗證是不是合法 ENUM 值
    bankaccount: str
    bankid: str
    bankpassword: str

class BankConnectionOut(BaseModel):
    id: int
    user_id: int
    provider: str
    bankaccount: str
    bankid: str
    last_update: datetime
    create_date: datetime

    class Config:
        from_attributes = True
