from dotenv import load_dotenv
import os
from datetime import date, timedelta
import random
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Account, Transaction

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# DB setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Faker
fake = Faker()

# Mappings
TRANSACTION_CATEGORIES = {
    "Grocery": ["King Soopers", "Safeway", "Target", "Trader Joe's", "Whole Foods", "Walmart"],
    "Travel": ["Uber", "Lyft", "RTD"],
    "Bills": ["Xfinity Wi-fi", "Electricity Bill", "Maintenance Bill", "Utilities"],
    "Shopping": ["H&M", "Marshalls", "Ross", "Nike", "Adidas", "Walmart"],
    "Dining": ["Subway", "McDonald's", "Chipotle", "Cane's", "BJ's", "Burger King", "Dominos"],
    "Entertainment": ["Netflix", "Amazon Prime", "Hulu", "Disney Plus"],
    "Health": ["Target", "CVS Pharmacy", "Walmart"]
}

CHECKING_OPTIONS = ["Wells Fargo", "Chase", "1st Bank", "Bank of America", "Capital One"]
SAVINGS_OPTIONS = CHECKING_OPTIONS
CREDIT_OPTIONS = CHECKING_OPTIONS + ["Amex Gold", "Amex Business", "Amex Delta", "Discover"]

def create_users_and_data():
    Base.metadata.create_all(bind=engine)

    for i in range(10):
        # Create user
        user = User(
            user_name=fake.name(),
            user_email=fake.unique.email(),
            user_is_premium=False
        )
        session.add(user)
        session.commit()

        accounts = []

        # Checking + Savings
        checking = Account(user_id=user.user_id, account_name=random.choice(CHECKING_OPTIONS), account_type="checking", account_balance=0.0)
        savings = Account(user_id=user.user_id, account_name=random.choice(SAVINGS_OPTIONS), account_type="savings", account_balance=0.0)
        accounts.extend([checking, savings])

        # Two credit accounts
        for _ in range(2):
            credit = Account(
                user_id=user.user_id,
                account_name=random.choice(CREDIT_OPTIONS),
                account_type="credit",
                account_balance=round(random.uniform(-50, 0), 2)
            )
            accounts.append(credit)

        session.add_all(accounts)
        session.commit()

        # Transactions
        txn_count = 100
        for _ in range(txn_count):
            account = random.choice(accounts)
            category = random.choice(list(TRANSACTION_CATEGORIES.keys()))
            name = random.choice(TRANSACTION_CATEGORIES[category])
            amount = round(random.uniform(5, 300), 2)
            txn_date = date.today() - timedelta(days=random.randint(0, 30))

            txn = Transaction(
                account_id=account.account_id,
                transaction_name=name,
                transaction_amount=amount,
                transaction_category=category,
                transaction_date=txn_date
            )
            session.add(txn)

            # Adjust account balance
            if account.account_type == "credit":
                account.account_balance -= amount
            else:
                account.account_balance += amount

        session.commit()

if __name__ == "__main__":
    create_users_and_data()
