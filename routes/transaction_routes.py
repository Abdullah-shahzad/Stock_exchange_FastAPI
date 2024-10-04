from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from models.transaction import Transaction
from models.stock import Stocks
from models.users import Users
from schemas.transaction_schema import TransactionCreate,TransactionResponse,TransactionBase
from datetime import datetime

transaction_router = APIRouter()


@transaction_router.post("/transactions", response_model=TransactionCreate, status_code=status.HTTP_201_CREATED)
async def create_transaction(
        transaction: transaction_schema,
        db: Session = Depends(get_db)
):
    """
    Creates a new transaction (buy/sell stocks), checks balance, updates accordingly.
    """
    stock = db.query(Stocks).filter(Stocks.id == Transaction.ticker_id).first()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    transaction_price = stock.stock_price * Transaction.transaction_volume

    if Transaction.transaction_type == 'BUY':
        if Users.balance < transaction_price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        Users.balance -= transaction_price
    elif Transaction.transaction_type == 'SELL':
        Users.balance += transaction_price

    db.add(transaction(
        user_id=Users.id,
        ticker_id=Transaction.ticker_id,
        transaction_price=transaction_price,
        transaction_volume=Transaction.transaction_volume,
        transaction_type=Transaction.transaction_type
    ))
    db.commit()

    return {"msg": "Transaction created successfully"}


@transaction_router.get("/transactions/{username}",
                        response_model=list[TransactionResponse],
                        status_code=status.HTTP_200_OK)
async def list_user_transactions(username: str, db: Session = Depends(get_db)):
    """
    Lists all transactions for a specific user.
    """
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = db.query(Transaction).filter(Transaction.user_id == Users.id).all()
    return transactions


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
