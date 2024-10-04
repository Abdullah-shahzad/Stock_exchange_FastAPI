from fastapi import FastAPI
from routes import user_routes, stock_routes,transaction_routes

app = FastAPI()

app.include_router(user_routes.user_router)
app.include_router(stock_routes.router)
app.include_router(transaction_routes.transaction_router)