from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from db import SessionLocal
from models import User, Account, Transaction

from fastapi import HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/ping")
def ping(db: Session = Depends(get_db)):
    return {"message": "Database connected!"}

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "user_id": user.user_id,
            "email": user.user_email,
            "name": user.user_name,
            "is_premium": user.user_is_premium
        }
        for user in users
    ]

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        return {"error": "User not found"}
    return {
        "user_id": user.user_id,
        "user_email": user.user_email,
        "user_name": user.user_name,
        "user_is_premium": user.user_is_premium
    }

@router.get("/users/{user_id}/accounts")
def get_user_accounts(user_id: int, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    response = []

    for acc in accounts:
        balance = (
            db.query(func.sum(Transaction.transaction_amount))
            .filter(Transaction.account_id == acc.account_id)
            .scalar()
            or 0.0
        )
        response.append({
            "account_id": acc.account_id,
            "account_name": acc.account_name,
            "account_type": acc.account_type,
            "account_balance": round(balance, 2)
        })

    return response

@router.get("/users/{user_id}/transactions")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [acc.account_id for acc in accounts]

    transactions = db.query(Transaction).filter(
        Transaction.account_id.in_(account_ids)
    ).order_by(Transaction.account_id).all()

    return [
        {
            "transaction_id": txn.transaction_id,
            "account_id": txn.account_id,
            "account_type": txn.account.account_type,
            "bank_name": txn.account.account_name,
            "transaction_name": txn.transaction_name,
            "transaction_amount": txn.transaction_amount,
            "transaction_category": txn.transaction_category,
            "transaction_date": txn.transaction_date
        }
        for txn in transactions
    ]


class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify against fixed '123456' for now
    if not pwd_context.verify(payload.password, pwd_context.hash("123456")):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"user_id": user.user_id, "user_name": user.user_name, "user_is_premium": user.user_is_premium}
