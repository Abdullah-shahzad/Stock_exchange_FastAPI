from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    ticker_id: int = Field(..., description="ID of the stock being transacted")
    transaction_volume: int = Field(..., description="Volume of the stock being transacted")
    transaction_type: str = Field(..., description="Type of transaction: BUY or SELL")
    transaction_price: float = Field(..., description="Price at which the transaction occurs")
    user_id: int = Field(..., description="ID of the user making the transaction")

class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction.
    """
    pass

class TransactionResponse(TransactionBase):
    """
    Schema for retrieving a transaction.
    """
    id: int = Field(..., description="Unique identifier for the transaction")
    created_time: datetime = Field(..., description="Timestamp when the transaction was created")

    class Config:
        orm_mode = True  # This allows compatibility with SQLAlchemy models
