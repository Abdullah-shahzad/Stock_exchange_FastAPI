from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from common.authentication import get_current_user
from config.logger import logger
from config.tasks import notify_new_stock
from models.stock import Stocks
from schemas.stock_schema import StockCreate, StockResponse
from database.db import get_db

router = APIRouter()


@router.post("/stocks/", response_model=StockResponse)
async def create_stock(
        stock: StockCreate,
        db: AsyncSession = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    # Use select for async queries
    result = await db.execute(select(Stocks).filter(Stocks.ticker == stock.ticker))
    existing_stock = result.scalars().first()

    if existing_stock:
        raise HTTPException(status_code=400, detail="Stock with this ticker already exists")

    if stock.stock_price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")

    logger.info(f"creating new stock {stock.ticker}")

    db_stock = Stocks(
        ticker=stock.ticker,
        stock_name=stock.stock_name,
        stock_price=stock.stock_price
    )

    # Notify asynchronously (assumed to be compatible with async)
    notify_new_stock.delay(stock.ticker, stock.stock_name, stock.stock_price)

    db.add(db_stock)
    await db.commit()  # Await commit
    await db.refresh(db_stock)  # Await refresh

    return db_stock


@router.get("/stocks/", response_model=list[StockResponse])
async def list_stocks(db: AsyncSession = Depends(get_db)):
    logger.info("Listing all the stocks")
    try:
        result = await db.execute(select(Stocks))
        stocks = result.scalars().all()
        return stocks
    except Exception as e:
        logger.error(f"Error: {e}")
        return []




@router.get("/stocks/{ticker}", response_model=StockResponse)
async def get_stock(ticker: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"getting stock {ticker}")
    stock = await db.execute(select(Stocks).filter(Stocks.ticker == ticker))
    stock = stock.scalars().first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock
