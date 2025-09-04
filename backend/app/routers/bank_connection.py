# app/routers/bank_connection.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.database.db import get_db
from app.models.bank_connection import BankConnection as DBBankConnection
from app.models.user import User
from app.schemas.bank_connection import BankConnectionCreate, BankConnectionOut
from app.utils.security import get_current_user
from datetime import datetime, timezone

import subprocess
import os
import json

from pydantic import BaseModel

router = APIRouter(prefix="/bank-connections", tags=["bank_connections"])

@router.post("/", response_model=BankConnectionOut, status_code=status.HTTP_201_CREATED)
def create_bank_connection(
    bank: BankConnectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 同 user + provider + bankaccount 不可重複
    dup = (
        db.query(DBBankConnection)
        .filter(
            DBBankConnection.user_id == user.id,
            DBBankConnection.provider == bank.provider,
            DBBankConnection.bankaccount == bank.bankaccount,
        )
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This bank account is already linked for this provider",
        )

    row = DBBankConnection(
        user_id=user.id,
        provider=bank.provider,
        bankaccount=bank.bankaccount,
        bankid=bank.bankid,
        bankpassword=bank.bankpassword,  
    )

    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicated bank connection")

    return row


@router.get("/", response_model=list[BankConnectionOut])
def list_bank_connections(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
  
    rows = (
        db.query(DBBankConnection)
        .filter(DBBankConnection.user_id == user.id)
        .all()
    )

    for row in rows:
        print(f"bccash: {row.BcCash}, bcmainaccount: {row.BcMainaccount}")
    
    return rows


BASE_DIR = "/home/ty/Desktop/Property/bankhub/backend/app/mypython"

PROVIDER_SCRIPT_MAP = {
    "LINE_BANK": "FetchLinebank.py",
    "ESUN_BANK": "FetchEsunbank.py",
    # 之後要擴充就在這裡加
}

def _resolve_script(provider: str) -> str:
    if not provider:
        raise HTTPException(status_code=400, detail="provider is required")
    key = provider.strip().upper()
    script_name = PROVIDER_SCRIPT_MAP.get(key)
    if not script_name:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.isfile(script_path):
        raise HTTPException(status_code=500, detail=f"Script not found: {script_path}")
    return script_path

class UpdateCashIn(BaseModel):
    account: str
    password: str
    id: str   
    provider: str

@router.post("/update_cash")
async def update_cash(
    payload: UpdateCashIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    account = payload.account
    password = payload.password
    bank_conn_id = payload.id
    provider = payload.provider

    script_path = _resolve_script(provider)


    result = subprocess.run(
        ['python3', script_path, account, password, bank_conn_id],
        capture_output=True, text=True
    )
    print(result)
    if result.returncode == 0:
        try:
            print(f"[DEBUG] Script output: {result.stdout}")  # 打印腳本輸出的內容
            result_data = json.loads(result.stdout)

            account_name = result_data.get("account_name")
            available_balance = result_data.get("available_balance")

            conn = (
                db.query(DBBankConnection)
                #確認該bankCard
                .filter(
                    DBBankConnection.bankid == bank_conn_id,   
                    DBBankConnection.provider == provider, 
                )
                .one_or_none()
            )
            if not conn:
                raise HTTPException(status_code=404, detail="Bank connection not found")

            conn.last_update = datetime.now(timezone.utc) 
            conn.BcCash = int(available_balance.replace(",", ""))  # 去掉千分位後轉整數
            conn.BcMainaccount = str(account_name)

            # conn.cash = available_balance
            db.commit()
            db.refresh(conn)

            return {
                "message": "Cash updated successfully",
                "account_name": account_name,
                "available_balance": available_balance,
            }

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse the response from the script")
    else:
        raise HTTPException(status_code=500, detail=result.stderr)



#==================================================================#
#讓後端爬蟲程式取得銀行的帳號密碼                                    #
#==================================================================#
@router.get("/line_bank", response_model=dict)
def get_line_bank_account(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    查詢目前登入者在 provider=LINE_BANK 下的銀行帳號資料。
    """
    bank_connection = db.query(DBBankConnection).filter(
        DBBankConnection.user_id == user.id,
        DBBankConnection.provider == "LINE_BANK"
    ).first()

    if not bank_connection:
        raise HTTPException(status_code=404, detail="No bank connection found for LINE_BANK")

    # 返回銀行帳號的資料
    return {
        "bankaccount": bank_connection.bankaccount,
        "bankid": bank_connection.bankid,
        "bankpassword": bank_connection.bankpassword
    }

@router.get("/esun_bank", response_model=dict)
def get_line_bank_account(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    查詢目前登入者在 provider=LINE_BANK 下的銀行帳號資料。
    """
    bank_connection = db.query(DBBankConnection).filter(
        DBBankConnection.user_id == user.id,
        DBBankConnection.provider == "ESUN_BANK"
    ).first()

    if not bank_connection:
        raise HTTPException(status_code=404, detail="No bank connection found for LINE_BANK")

    # 返回銀行帳號的資料
    return {
        "bankaccount": bank_connection.bankaccount,
        "bankid": bank_connection.bankid,
        "bankpassword": bank_connection.bankpassword
    }

#==================================================================#
#刪除當前使用者 當前BANK Provider、BANK ID的資料 (只會有唯一資料被刪除)#
#==================================================================#

@router.delete("/{provider}/{bankid}")
async def delete_bank_connection(provider: str, bankid: str, db: Session = Depends(get_db)):
    print(f"Deleting bank connection: provider={provider}, bankid={bankid}")
    
    # 查詢資料庫中的資料
    bank = db.query(DBBankConnection).filter(
        DBBankConnection.provider == provider,
        DBBankConnection.bankid == bankid
    ).first()

    if not bank:
        raise HTTPException(status_code=404, detail="Bank connection not found")

    db.delete(bank)
    db.commit()
    return {"message": "Bank connection deleted successfully"}




