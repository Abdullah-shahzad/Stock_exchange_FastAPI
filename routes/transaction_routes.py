from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from common.authentication import get_current_user
from config.logger import logger
from database.db import get_db
from models.transaction import Transaction
from models.stock import Stocks
from models.users import Users
from schemas.transaction_schema import TransactionCreate, TransactionResponse
from datetime import datetime

transaction_router = APIRouter()


@transaction_router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
        transaction: TransactionCreate,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    """
    Creates a new transaction (buy/sell stocks), checks balance, updates accordingly.
    """
    logger.info("Creating new transaction ")
    if transaction.transaction_volume <= 0:
        raise HTTPException(status_code=404, detail="Volume must be greater than 0")

    if transaction.transaction_type not in ["BUY","SELL","Buy","Sell","sell","buy"]:
        raise HTTPException(status_code=404, detail="Transaction type must be BUY or SELL")

    stock = db.query(Stocks).filter(Stocks.ticker == transaction.ticker).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Query user by username
    user = db.query(Users).filter(Users.username == transaction.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    # Calculate transaction price
    transaction_price = stock.stock_price * transaction.transaction_volume

    if transaction.transaction_type == 'BUY' or 'Buy' or 'buy':
        if user.balance < transaction_price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        user.balance -= transaction_price
    elif transaction.transaction_type == 'SELL' or 'Sell' or 'sell':
        user.balance += transaction_price

    new_transaction = Transaction(
        user_id=user.id,
        ticker_id=stock.id,
        transaction_price=transaction_price,
        transaction_volume=transaction.transaction_volume,
        transaction_type=transaction.transaction_type
    )

    # Add and commit the transaction
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # Prepare the response
    response = TransactionResponse(
        id=new_transaction.id,
        transaction_volume=new_transaction.transaction_volume,
        transaction_type=new_transaction.transaction_type,
        transaction_price=new_transaction.transaction_price,
        created_time=new_transaction.created_time,
        username=user.username,
        ticker=stock.ticker
    )

    return response


@transaction_router.get("/transactions/", response_model=list[TransactionResponse])
def list_transaction(db: Session = Depends(get_db)):
    list_trans = db.query(Transaction).all()

    logger.info("List all the transactions")

    response = []
    for transaction in list_trans:
        user = db.query(Users).filter(Users.id == transaction.user_id).first()
        stock = db.query(Stocks).filter(Stocks.id == transaction.ticker_id).first()
        response.append(TransactionResponse(
            id=transaction.id,
            transaction_volume=transaction.transaction_volume,
            transaction_type=transaction.transaction_type,
            transaction_price=transaction.transaction_price,
            created_time=transaction.created_time,
            username=user.username if user else None,  # Handle possible None
            ticker=stock.ticker if stock else None       # Handle possible None
        ))

    return response


@transaction_router.get("/transactions/{username}/by-date", response_model=list[TransactionResponse],
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

    logger.info("Listing transactions by timestamp")
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        start_timestamp = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_timestamp = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id,  # Filter transactions by user ID
        Transaction.created_time.between(start_timestamp, end_timestamp)
    ).all()

    return transactions

@transaction_router.get("/transactions/user/{username}", response_model=list[TransactionResponse], status_code=status.HTTP_200_OK)
async def get_transactions_by_username(username: str, db: Session = Depends(get_db)):
    """
    Retrieve all transactions for a specific user identified by their username.
    """
    logger.info("Retrieving transactions by username")

    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).all()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")


    response = []
    for transaction in transactions:
        response.append(TransactionResponse(
            id=transaction.id,
            transaction_volume=transaction.transaction_volume,
            transaction_type=transaction.transaction_type,
            transaction_price=transaction.transaction_price,
            created_time=transaction.created_time,
            username=user.username,
            ticker=transaction.ticker.ticker
        ))

    return response


