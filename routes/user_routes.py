from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from common.authentication import get_password_hash
from models.users import Users
from schemas.user_schema import UserCreate, UserResponse
from database.db import get_db

user_router = APIRouter()


@user_router.post("/register", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = Users(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@user_router.get("/users/{username}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(username: str, db: Session = Depends(get_db)):
    """
    Retrieves user details by username.
    """
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

