# app/schemas/bank_connection.py
from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional

class BankConnectionCreate(BaseModel):
    provider: str        
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

    BcCash: Optional[int] = None
    BcMainaccount: Optional[str] = None
    BcStock: Optional[int] = None


    class Config:
        from_attributes = True
