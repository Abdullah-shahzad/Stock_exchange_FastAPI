from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    balance: float

class UserResponse(BaseModel):
    username: str
    balance: float

    class Config:
        orm_mode = True
