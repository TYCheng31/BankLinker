import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 讀取資料庫 URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kevin:kevin@localhost:5432/bankuser")

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# 用於生成和驗證 JWT 的密鑰和算法
#JWT_SECRET_KEY=Jv8sQw2rT9pXz1Lk6bNf4eHc7Yg5Wm3Zq0Vt9Rj2Uo8Sx5Pq
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "JWT_SECRET_KEY=Jv8sQw2rT9pXz1Lk6bNf4eHc7Yg5Wm3Zq0Vt9Rj2Uo8Sx5Pq")  # 建議放在 .env
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60