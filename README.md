# Capital Bank — Web-based Online Banking Simulator

A web-based banking simulator built with Flask and MySQL. Users can register, log in, move money between accounts, and manage their profile and security settings.

> This is a learning project. It is a simulator and is not meant for real money.

## Features

- Registration with an automatically generated unique 16-digit account number
- Login with phone number and password
- Dashboard with current balance and the 3 most recent transactions
- Deposit and withdraw (authorised with a 4-digit transaction PIN)
- Transfer money by account number or by phone number
- Full transaction history (credit/debit, counterparty, remarks)
- Account details, update profile, change password, change transaction PIN
- Logout

## Security

- Passwords and transaction PINs are stored hashed (passlib `sha256_crypt`)
- CSRF protection on all forms (Flask-WTF)
- Parameterised SQL queries throughout
- Withdrawals and transfers check the balance inside the `UPDATE` statement itself, so two simultaneous requests cannot overdraw an account
- Money is stored as `DECIMAL(12,2)`, and the database also enforces `balance >= 0`
- 5 wrong PIN attempts or 5 wrong password attempts lock that credential for 15 minutes
- Users can only edit their own profile
- Secrets are loaded from a `.env` file that is not committed

## Tech stack

Python, Flask, Flask-WTF / WTForms, MySQL (`mysql-connector-python`), passlib, HTML, CSS, JavaScript

## Setup

1. **Clone the repository and enter it**

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create the database** (needs a running MySQL server)

   ```bash
   mysql -u <your-mysql-user> -p < schema.sql
   ```

   This creates the `capital_bank` database and its three tables (`users`, `accounts`, `transactions`).

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Open `.env` and fill in your MySQL details. Generate a secret key with:

   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Run the app**

   ```bash
   python app.py
   ```

   Then open <http://127.0.0.1:5000>.

> `app.py` runs with `debug=True` for development. Turn it off before running the app anywhere other than your own machine.

## Notes for using the app

- New accounts start with a balance of Rs 1,000.
- Phone numbers must be 10 digits starting with 97 or 98.
- Transaction amounts must be between Rs 10 and Rs 100,000, with at most 2 decimal places.
- The transaction PIN is exactly 4 digits.
- Passwords need 8–64 characters, with at least one letter, one number and one special character.

## Project structure

```
app.py                 Flask app setup and blueprint registration
database.py            MySQL connection helper
schema.sql             Database schema
routes/
  auth.py              Register, login, logout
  main.py              Dashboard, transaction history, settings page
  transactions.py      Deposit, withdraw, transfers
  settings.py          Account details, change password/PIN, update profile
forms/                 WTForms form classes and validators
utils/
  decorators.py        Login-required decorator
  security.py          PIN/password verification with lockout
  transaction_history.py  Builds the history rows shown to the user
templates/             Jinja2 templates
static/                CSS and JavaScript
```

## Known limitations and future work

- No "forgot password" or "forgot PIN" recovery flow
- No admin panel (user management, account unlock, teller-style deposits)
- No email or SMS notifications
- Login attempts are limited per account only, not per IP address
- Account deletion is not implemented yet
- No automated tests