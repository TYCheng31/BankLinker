# app/models/bank_connection.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base
from sqlalchemy.dialects.postgresql import ENUM as PGEnum



class BankConnection(Base):
    __tablename__ = "bank_connections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    provider = Column(PGEnum('ESUN_BANK', 'CATHAY_BANK', 'LINE_BANK', name='bank_provider', create_type=False), nullable=False)
    
    bankaccount = Column(String, nullable=False)
    bankid = Column(String, nullable=False)
    bankpassword = Column(String, nullable=False)  

    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    create_date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bank_connections")
