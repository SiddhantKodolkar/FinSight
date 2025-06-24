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
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_premium": user.is_premium
        }
        for user in users
    ]

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return {"error": "User not found"}
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "is_premium": user.is_premium
    }

@router.get("/users/{user_id}/accounts")
def get_user_accounts(user_id: int, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    response = []
    for acc in accounts:
        balance = db.query(func.sum(Transaction.amount)).filter(Transaction.account_id == acc.id).scalar() or 0.0
        response.append({
            "id": acc.id,
            "name": acc.name,
            "type": acc.type,
            "balance": round(balance, 2)
        })
    return response

@router.get("/users/{user_id}/transactions")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == str(user_id)).all()
    account_ids = [acc.id for acc in accounts]

    transactions = db.query(Transaction).filter(
        Transaction.account_id.in_(account_ids)
    ).order_by(Transaction.account_id).all()

    return [
        {
            "transaction_id": txn.id,
            "account_id": txn.account_id,
            "type": txn.account.type,
            "bank": txn.account.name,
            "name": txn.name,
            "amount": txn.amount,
            "category": txn.category,
            "date": txn.date
        }
        for txn in transactions
    ]


class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify against fixed '123456' for now
    if not pwd_context.verify(payload.password, pwd_context.hash("123456")):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"user_id": user.id, "name": user.name, "is_premium": user.is_premium}
