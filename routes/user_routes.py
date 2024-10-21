from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from common.authentication import get_password_hash, pwd_context, create_access_token, verify_password
from config.logger import logger
from models.users import Users
from schemas.user_schema import UserCreate
from database.db import get_db

user_router = APIRouter()

@user_router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Creating a new user.
    """
    logger.info("Registering new user")

    # Check if the username already exists
    existing_user_query = select(Users).where(Users.username == user.username)
    result = await db.execute(existing_user_query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if user.balance <= 0:
        raise HTTPException(status_code=400, detail="Balance must be greater than zero")

    # Hash the password and create the user
    hashed_password = pwd_context.hash(user.password)
    new_user = Users(
        username=user.username,
        hashed_password=hashed_password,
        balance=user.balance
    )

    try:
        db.add(new_user)
        await db.commit()  # Await the commit
        await db.refresh(new_user)  # Await the refresh
        return {"message": "User created successfully", "user_id": new_user.id}
    except IntegrityError:
        await db.rollback()  # Await rollback
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")


@user_router.get("/users/{username}")
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    # Use select to query the user
    query = select(Users).where(Users.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()  # Get a single user or None

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
