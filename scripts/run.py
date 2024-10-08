from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from common.authentication import verify_password, create_access_token, get_password_hash
from database.db import get_db
from models.users import Users
from routes import user_routes, stock_routes, transaction_routes

app = FastAPI()

app.include_router(user_routes.user_router)
app.include_router(stock_routes.router)
app.include_router(transaction_routes.transaction_router)



@app.post("/login")
async def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(Users).filter_by(username=form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}




# @app.post("/login")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
# async def login(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(Users).filter_by(username=user.username).first()
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     access_token = create_access_token(data={"sub": db_user.username})
#     return {"access_token": access_token, "token_type": "bearer"}


    # user = users_db.get(form_data.username)
    # if not user or not verify_password(form_data.password, user['hashed_password']):
    #     raise HTTPException(status_code=400, detail="Invalid username or password")
    #
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)
    #
    # return {"access_token": access_token, "token_type": "bearer"}
