from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import DATABASE_URL

# 資料庫連線設置
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 用來建立 DB 連接的會話（Session）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()