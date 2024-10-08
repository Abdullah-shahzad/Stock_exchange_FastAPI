from pydantic import BaseModel, Field
from datetime import datetime

class TransactionBase(BaseModel):
    username: str = Field(..., description="Username of the user making the transaction")
    ticker: str = Field(..., description="Ticker symbol of the stock being transacted")
    transaction_volume: int = Field(..., description="Volume of the stock being transacted")
    transaction_type: str = Field(..., description="Type of transaction: BUY or SELL")
    transaction_price: float = Field(..., description="Price at which the transaction occurs")

class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction.
    """
    pass

class TransactionResponse(BaseModel):
    id: int
    transaction_volume: float
    transaction_type: str
    transaction_price: float
    created_time: datetime
    username: str
    ticker: str

    class Config:
        from_attributes = True
