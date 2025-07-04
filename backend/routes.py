from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from db import SessionLocal
from models import User, Account, Transaction
from sqlalchemy.sql import extract
from fastapi import HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import stripe


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
            "user_email": user.user_email,
            "user_name": user.user_name,
            "user_is_premium": user.user_is_premium
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

    return {
    "user_id": user.user_id,
    "user_name": user.user_name,
    "user_email": user.user_email,  # ✅ must be included
    "user_is_premium": user.user_is_premium
    }



class CheckoutRequest(BaseModel):
    user_id: int

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    try:
        data = await request.json()
        user_email = data.get("email")

        if not user_email:
            raise HTTPException(status_code=400, detail="Email is required")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user_email,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "FinSight Premium"},
                    "unit_amount": 499,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:3000/premium-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/dashboard",
        )

        return {"checkout_url": session.url}

    except Exception as e:
        print("Stripe error:", e)
        raise HTTPException(status_code=500, detail="Stripe Checkout session creation failed")



@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except stripe.error.SignatureVerificationError as e:
        print("❌ Webhook signature failed")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    print("✅ Webhook received:", event["type"])

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]
        customer_email = session_data.get("customer_email")
        print("➡️ Checkout completed for:", customer_email)

        user = db.query(User).filter(User.user_email == customer_email).first()
        if user:
            user.user_is_premium = True
            db.commit()
            print("✅ User marked as premium:", user.user_email)
        else:
            print("⚠️ No user found with that email")

    return {"status": "success"}


@router.get("/users/{user_id}/insights")
def get_user_insights(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    account_ids = [acc.account_id for acc in accounts]

    insights = {}

    # Weekly spending with week range formatting and % change
    raw_weeks = db.query(
        func.date_trunc('week', Transaction.transaction_date).label("week_start"),
        func.sum(Transaction.transaction_amount).label("total")
    ).filter(Transaction.account_id.in_(account_ids)).group_by("week_start").order_by("week_start").all()

    weekly_spending = []
    for i, row in enumerate(raw_weeks):
        start = row.week_start
        end = start + timedelta(days=6)
        total = round(row.total, 2)

        percent_change = None
        if i > 0:
            prev_total = round(raw_weeks[i - 1].total, 2)
            if prev_total > 0:
                percent_change = round(((total - prev_total) / prev_total) * 100, 1)

        weekly_spending.append({
            "range": f"{start.strftime('%b %d')} – {end.strftime('%b %d')}",
            "total": total,
            "change": percent_change
        })

    insights["weekly_spending"] = weekly_spending

    # Top categories
    category_data = db.query(
        Transaction.transaction_category,
        func.sum(Transaction.transaction_amount).label("total")
    ).filter(Transaction.account_id.in_(account_ids)).group_by(Transaction.transaction_category).order_by(func.sum(Transaction.transaction_amount).desc()).limit(5).all()

    insights["top_categories"] = [
        {"category": row.transaction_category, "total": round(row.total, 2)} for row in category_data
    ]

    # Top merchants
    merchant_data = db.query(
        Transaction.transaction_name,
        func.sum(Transaction.transaction_amount).label("total")
    ).filter(Transaction.account_id.in_(account_ids)).group_by(Transaction.transaction_name).order_by(func.sum(Transaction.transaction_amount).desc()).limit(5).all()

    insights["top_merchants"] = [
        {"merchant": row.transaction_name, "total": round(row.total, 2)} for row in merchant_data
    ]

    # Average transaction
    avg_value = db.query(func.avg(Transaction.transaction_amount)).filter(Transaction.account_id.in_(account_ids)).scalar()
    insights["average_transaction"] = round(avg_value or 0.0, 2)

    # Flag unusually expensive transactions
    expensive = db.query(Transaction).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.transaction_amount > 250
    ).order_by(Transaction.transaction_amount.desc()).limit(5).all()

    insights["expensive_transactions"] = [
        {
            "name": tx.transaction_name,
            "amount": round(tx.transaction_amount, 2),
            "category": tx.transaction_category,
            "date": tx.transaction_date
        } for tx in expensive
    ]

    return insights