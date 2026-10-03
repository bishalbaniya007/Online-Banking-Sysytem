from flask import Blueprint, render_template, session, flash
from utils.decorators import is_logged_in
from database import get_db_connection
from utils.transaction_history import build_txn_history

main = Blueprint("main", __name__)

# DASHBOARD
@main.route("/dashboard")
@is_logged_in
def dashboard():
  user_id = session.get('user_id')
  balance = 0.00    # Fall back in case of database error
  account_num = None  # Fall back in case of database error

  db = get_db_connection()
  cursor = db.cursor(dictionary=True)

  recent_transactions = []    # LIST OF DICTIONARIES
  try:
    # fetch the balance, account_id of current user
    cursor.execute("SELECT balance, account_id, account_num FROM accounts WHERE user_id = %s", (user_id,))
    user_account = cursor.fetchone()
    balance = user_account["balance"]
    user_acc_id = user_account["account_id"]
    account_num = user_account["account_num"]

    # getting the last 3 transasctions involving this account_id
    cursor.execute("""
          SELECT * FROM transactions 
          WHERE sender_acc_id = %s OR receiver_acc_id = %s
          ORDER BY transaction_date DESC
          LIMIT 3""", (user_acc_id, user_acc_id))

    recent_transactions = cursor.fetchall()

    for transaction in recent_transactions:
      build_txn_history(cursor, transaction, user_acc_id)

  except Exception as e:
    flash("An unexpected database error occured. Please try again.", "danger")
    print(f"Error Loading Dashboard: {e}")

  finally:
    cursor.close()
    db.close()

  return render_template("dashboard.html", title="Dashboard", balance=balance, transactions = recent_transactions, account_num=account_num)


# TRANSFER MENU OPTIONS
@main.route("/transfer")
@is_logged_in
def transfer():
  return render_template("transfer_menu.html", title="Transfer")

# Transaction History Page
@main.route("/history")
@is_logged_in
def history():
  # 1.getting user_id from the session
  user_id = session.get('user_id')

  db = get_db_connection()
  cursor = db.cursor(dictionary=True)

  result = []   # list of dictionaries
  try:
    # 2. getting user's account id
    cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
    user_acc_id = cursor.fetchone()['account_id']

    # 3. getting all transactions involving this account
    cursor.execute("""
          SELECT * FROM transactions
          WHERE sender_acc_id = %s OR receiver_acc_id = %s
          ORDER BY transaction_date DESC
          """, (user_acc_id, user_acc_id))

    result = cursor.fetchall()

    # 4. For each transaction:
    for transaction in result:
      build_txn_history(cursor, transaction, user_acc_id)
    
  except Exception as e:
    flash("An unexpected error occured. Please try again.", "danger")
    print(f"Transction history error: {e}")

  finally:
    cursor.close()
    db.close()

  return render_template("transaction_history.html", title="Transaction History", transactions=result)

# Settings page
@main.route("/settings")
@is_logged_in
def settings():
  return render_template("settings.html", title="Settings")