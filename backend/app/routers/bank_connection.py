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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    #for row in rows:
        #print(f"bccash: {row.BcCash}, bcmainaccount: {row.BcMainaccount}, bcstock: {row.BcStock}")
    
    return rows


BASE_DIR = "/home/kevin/Desktop/BankLinker/bankhub/backend/app/mypython"

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
            stock = result_data.get('stock') if provider == "ESUN_BANK" else 0
            #print(stock)
            # 確保 available_balance 是字串並可以進行 replace() 操作
            if isinstance(available_balance, str):
                if available_balance.replace(",", "").isdigit():
                    available_balance = int(available_balance.replace(",", ""))
                else:
                    raise HTTPException(status_code=400, detail="無效的可用餘額格式")
            elif isinstance(available_balance, int):
                # 如果 available_balance 已經是整數，則直接使用它
                available_balance = available_balance
            else:
                raise HTTPException(status_code=400, detail="無效的可用餘額格式")

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
                raise HTTPException(status_code=404, detail="找不到該銀行連接")

            conn.last_update = datetime.now(timezone.utc) 
            conn.BcCash = available_balance  # 使用有效的可用餘額
            conn.BcMainaccount = str(account_name)
            conn.BcStock = int(stock) if provider == "ESUN_BANK" else 0

            db.commit()
            db.refresh(conn)

            response = {
                "message": "現金更新成功",
                "account_name": account_name,
                "available_balance": available_balance,
            }
            if stock is not None:
                response["stock"] = stock

            return response

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="解析腳本回應失敗")
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
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




class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

# 發送 Email 函數
def send_email(to: str, subject: str, body: str):
    from_email = "xiaochiprojectuse@gmail.com"  # 你的郵箱
    from_password = "chengxiaochi0331"  # 你的郵箱密碼

    # 設定 SMTP 伺服器
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # 建立一封郵件
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to
    msg['Subject'] = subject

    # 郵件內容
    msg.attach(MIMEText(body, 'plain'))

    try:
        # 連接到 Gmail 的 SMTP 伺服器
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # 開啟 TLS 加密
            server.login(from_email, from_password)  # 登錄郵箱
            text = msg.as_string()  # 將郵件訊息轉為字串
            server.sendmail(from_email, to, text)  # 發送郵件
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")


@router.post("/SendEmail")
async def send_email_api(email_request: EmailRequest):

    try:
        result = send_email(email_request.to, email_request.subject, email_request.body)
        return {"message": "Email sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")