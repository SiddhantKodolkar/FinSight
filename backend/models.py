from sqlalchemy import Column, Float, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, index=True)
    user_name = Column(String)
    user_is_premium = Column(Boolean, default=False)

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False) 
    account_name = Column(String)
    account_type = Column(String)
    account_balance = Column(Float)

    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    transaction_name = Column(String)
    transaction_amount = Column(Float)
    transaction_category = Column(String)
    transaction_date = Column(Date)

    account = relationship("Account", back_populates="transactions")
