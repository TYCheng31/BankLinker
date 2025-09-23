# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, echo, user, bank_connection, auth

app = FastAPI(title="BankHub API (dev)")

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://192.168.1.61:3000",
    "http://192.168.1.61:5173",
    "https://d7ebcce482fe.ngrok-free.app:3000",
    "https://d7ebcce482fe.ngrok-free.app:5173"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,      # 若你沒用 cookie，也可設 False
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(echo.router)
app.include_router(user.router)
app.include_router(bank_connection.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"ok": True}
