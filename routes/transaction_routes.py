from datetime import datetime

from common.authentication import get_current_user
from config.logger import logger
from database.db import get_db
from models.transaction import Transaction
from models.stock import Stocks
from models.users import Users
from schemas.transaction_schema import TransactionCreate, TransactionResponse
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

transaction_router = APIRouter()


@transaction_router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Creates a new transaction (buy/sell stocks), checks balance, updates accordingly.
    """
    logger.info("Creating new transaction")

    if transaction.transaction_volume <= 0:
        raise HTTPException(status_code=400, detail="Volume must be greater than 0")

    if transaction.transaction_type.lower() not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Transaction type must be BUY or SELL")

    # Use async query with select
    result = await db.execute(select(Stocks).filter(Stocks.ticker == transaction.ticker))
    stock = result.scalars().first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    result = await db.execute(select(Users).filter(Users.username == transaction.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transaction_price = stock.stock_price * transaction.transaction_volume

    if transaction.transaction_type.lower() == 'buy':
        if user.balance < transaction_price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        user.balance -= transaction_price
    else:  # For 'sell'
        user.balance += transaction_price

    new_transaction = Transaction(
        user_id=user.id,
        ticker_id=stock.id,
        transaction_price=transaction_price,
        transaction_volume=transaction.transaction_volume,
        transaction_type=transaction.transaction_type
    )

    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    return TransactionResponse(
        id=new_transaction.id,
        transaction_volume=new_transaction.transaction_volume,
        transaction_type=new_transaction.transaction_type,
        transaction_price=new_transaction.transaction_price,
        created_time=new_transaction.created_time,
        username=user.username,
        ticker=stock.ticker
    )

@transaction_router.get("/transactions/", response_model=list[TransactionResponse])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    logger.info("Listing all transactions")
    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()

    return [
        TransactionResponse(
            id=transaction.id,
            transaction_volume=transaction.transaction_volume,
            transaction_type=transaction.transaction_type,
            transaction_price=transaction.transaction_price,
            created_time=transaction.created_time,
            username=(await db.execute(select(Users).filter(Users.id == transaction.user_id))).scalars().first().username,
            ticker=(await db.execute(select(Stocks).filter(Stocks.id == transaction.ticker_id))).scalars().first().ticker
        ) for transaction in transactions
    ]


@transaction_router.get("/transactions/{username}/by-date", response_model=list[TransactionResponse],
                        status_code=status.HTTP_200_OK)
async def list_transactions_by_timestamp(
        username: str,
        start_time: str,
        end_time: str,
        db: AsyncSession = Depends(get_db)
):
    """
    Lists transactions by username, filtered by start and end timestamp.
    """
    logger.info("Listing transactions by timestamp")
    user_query = await db.execute(select(Users).filter(Users.username == username))
    user = user_query.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        start_timestamp = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_timestamp = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    transactions_query = await db.execute(
        select(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.created_time.between(start_timestamp, end_timestamp)
        )
    )
    transactions = transactions_query.scalars().all()

    return transactions


@transaction_router.get("/transactions/user/{username}", response_model=list[TransactionResponse],
                        status_code=status.HTTP_200_OK)
async def get_transactions_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve all transactions for a specific user identified by their username.
    """
    logger.info("Retrieving transactions by username")
    user_query = await db.execute(select(Users).filter(Users.username == username))
    user = user_query.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions_query = await db.execute(select(Transaction).filter(Transaction.user_id == user.id))
    transactions = transactions_query.scalars().all()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")

    return [
        TransactionResponse(
            id=transaction.id,
            transaction_volume=transaction.transaction_volume,
            transaction_type=transaction.transaction_type,
            transaction_price=transaction.transaction_price,
            created_time=transaction.created_time,
            username=user.username,
            ticker=transaction.ticker.ticker
        ) for transaction in transactions
    ]