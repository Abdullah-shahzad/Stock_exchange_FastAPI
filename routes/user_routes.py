from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from common.authentication import get_password_hash, pwd_context, create_access_token, verify_password
from models.users import Users
from schemas.user_schema import UserCreate, UserResponse
from database.db import get_db

user_router = APIRouter()



# @user_router.post("/login")
# async def login(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(Users).filter_by(username=user.username).first()
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     access_token = create_access_token(data={"sub": db_user.username})
#     return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the username already exists
    existing_user = db.query(Users).filter_by(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password and create the user
    hashed_password = pwd_context.hash(user.password)
    new_user = Users(
        username=user.username,
        hashed_password=hashed_password,
        balance=user.balance
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User created successfully", "user_id": new_user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the user")


@user_router.get("/users/{username}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(username: str, db: Session = Depends(get_db)):
    """
    Retrieves user details by username.
    """
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    return UserResponse(id=user.id, username=user.username, balance=user.balance)

