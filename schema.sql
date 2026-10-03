CREATE DATABASE IF NOT EXISTS capital_bank;

USE capital_bank;

CREATE TABLE IF NOT EXISTS users(
	user_id INT AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    transaction_pin VARCHAR(255) NOT NULL,
    phone VARCHAR(10) NOT NULL UNIQUE,
    failed_pin_attempts INT NOT NULL DEFAULT 0,
    pin_locked_until DATETIME NULL,
    failed_password_attempts INT NOT NULL DEFAULT 0,
    password_locked_until DATETIME NULL,
    PRIMARY KEY(user_id),
    CONSTRAINT chk_phone CHECK (length(phone) = 10)
);

CREATE TABLE IF NOT EXISTS accounts(
	account_id INT AUTO_INCREMENT,
    account_num VARCHAR(16) NOT NULL UNIQUE,
    balance DECIMAL(12, 2) NOT NULL DEFAULT 1000,
    user_id INT NOT NULL UNIQUE,
    PRIMARY KEY(account_id),
    FOREIGN KEY(user_id) references users(user_id),
    CONSTRAINT chk_balance CHECK (balance >= 0)
);

CREATE TABLE IF NOT EXISTS transactions(
	transaction_id INT AUTO_INCREMENT,
    amount DECIMAL(12,2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks VARCHAR(100) NOT NULL,
    sender_acc_id INT,
    receiver_acc_id INT,
    PRIMARY KEY(transaction_id),
    CONSTRAINT chk_amount CHECK(amount > 0),
    CONSTRAINT chk_transaction_type CHECK (transaction_type IN ('deposit', 'withdraw', 'transfer')),
    FOREIGN KEY (sender_acc_id) references accounts(account_id),
    FOREIGN KEY (receiver_acc_id) references accounts(account_id)
);










