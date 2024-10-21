CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(70) UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    balance FLOAT
);

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    stock_price FLOAT NOT NULL,
    stock_name VARCHAR(40)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    ticker_id INTEGER NOT NULL,
    transaction_type VARCHAR(4) DEFAULT 'BUY' NOT NULL,
    transaction_volume FLOAT NOT NULL,
    transaction_price FLOAT NOT NULL,
    created_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ticker_id) REFERENCES stocks(id) ON DELETE CASCADE
);
