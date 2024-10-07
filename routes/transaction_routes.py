from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.authentication import get_current_user
from database.db import get_db
from models.transaction import Transaction
from models.stock import Stocks
from models.users import Users
from schemas.transaction_schema import TransactionCreate, TransactionResponse
from datetime import datetime

transaction_router = APIRouter()


@transaction_router.post("/transactions", response_model=TransactionCreate, status_code=status.HTTP_201_CREATED)
async def create_transaction(
        transaction: TransactionCreate,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    """
    Creates a new transaction (buy/sell stocks), checks balance, updates accordingly.
    """
    stock = db.query(Stocks).filter(Stocks.id == transaction.ticker_id).first()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    transaction_price = stock.stock_price * transaction.transaction_volume

    user = db.query(Users).filter(Users.id == transaction.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if transaction.transaction_type == 'BUY':
        if user.balance < transaction_price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        user.balance -= transaction_price
    elif transaction.transaction_type == 'SELL':
        user.balance += transaction_price


    new_transaction = Transaction(
        user_id=transaction.user_id,
        ticker_id=transaction.ticker_id,
        transaction_price=transaction_price,
        transaction_volume=transaction.transaction_volume,
        transaction_type=transaction.transaction_type
    )

    # Add and commit the transaction
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@transaction_router.get("/transactions/", response_model=list[TransactionResponse])
def list_transaction(db: Session = Depends(get_db)):
    list_trans = db.query(Transaction).all()
    return list_trans


@transaction_router.get("/transactions/{username}/by-date",
                        response_model=list[TransactionResponse],
                        status_code=status.HTTP_200_OK)
async def list_transactions_by_timestamp(
    username: str,
    start_time: str,
    end_time: str,
    db: Session = Depends(get_db)
):
    """
    Lists transactions by username, filtered by start and end timestamp.
    """
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        start_timestamp = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_timestamp = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    transactions = db.query(Transaction).filter(
        Transaction.user_id == Users.id,
        Transaction.created_time.between(start_timestamp, end_timestamp)
    ).all()

    return transactions
