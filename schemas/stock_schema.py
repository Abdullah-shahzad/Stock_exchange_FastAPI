from pydantic import BaseModel

class StockCreate(BaseModel):
    ticker: str
    stock_name: str
    stock_price: float

class StockResponse(BaseModel):
    ticker: str
    stock_name: str
    stock_price: float

    class Config:
        orm_mode = True
