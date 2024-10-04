from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.stock import Stocks
from schemas.stock_schema import StockCreate, StockResponse
from database.db import get_db

router = APIRouter()

@router.post("/stocks/", response_model=StockResponse)
def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    db_stock = Stocks(ticker=Stocks.ticker, stock_name=Stocks.stock_name, stock_price=Stocks.stock_price)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.get("/stocks/", response_model=list[StockResponse])
def list_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stocks).all()
    return stocks

@router.get("/stocks/{ticker}", response_model=StockResponse)
def get_stock(ticker: str, db: Session = Depends(get_db)):
    stock = db.query(Stocks).filter(Stocks.ticker == ticker).first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock
