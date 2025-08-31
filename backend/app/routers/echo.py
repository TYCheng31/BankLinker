from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/echo", tags=["demo"])

class EchoIn(BaseModel):
    msg: str

@router.get("")
def echo_get(msg: str):
    return {"you_said": msg}

@router.post("")
def echo_post(payload: EchoIn):
    return {"you_said": payload.msg}
