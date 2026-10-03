from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from utils.decorators import is_logged_in
from forms.transaction_form import TransactionForm, AccountTransferForm, PhoneTransferForm
from database import get_db_connection
from passlib.hash import sha256_crypt
from utils.security import verify_pin

transactions = Blueprint("transactions", __name__)

# DEPOSIT MONEY
@transactions.route("/deposit", methods=["GET", "POST"])
@is_logged_in
def deposit():
  form = TransactionForm(request.form)

  if request.method == "POST" and form.validate():
    amount = form.amount.data
    remarks = form.remarks.data
    pin_input = form.transaction_pin.data
    user_id = session.get('user_id')

    db = get_db_connection()
    cursor = db.cursor()

    try:
      status = verify_pin(cursor, user_id, pin_input)
      if status == "ok":
        # updating the balance in accounts table
        cursor.execute("""
              UPDATE accounts
              SET balance = balance + %s
              WHERE user_id = %s """, (amount, user_id))

        # getting account id and inserting the transaction in transactions table
        cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
        account_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO transactions 
            (amount, transaction_type, remarks, receiver_acc_id) 
            VALUES 
            (%s, 'deposit', %s, %s)""", (amount, remarks, account_id))

        db.commit()

        flash(f"Successfully deposited Rs {amount:,.2f} to your account.", "success")
        return redirect(url_for('main.dashboard'))

      else:
        db.commit()
        if status == "locked":
          flash("Too many wrong attempts. Your account is locked for 15 minutes.", "danger")
        else:
          flash("Invalid transaction pin.", "danger")
     
    except Exception as e:
      db.rollback()
      flash("An unexpected database error occured. Please try again.", "danger")
      print(f"Deposit error: {e}")
      
    finally:
      cursor.close()
      db.close()

  return render_template("deposit_withdraw.html", title="Deposit", form=form, transaction_type="deposit")

# WITHDRAW MONEY
@transactions.route("/withdraw", methods=["GET", "POST"])
@is_logged_in
def withdraw():
  form = TransactionForm(request.form)

  if request.method == "POST" and form.validate():
    amount = form.amount.data
    remarks = form.remarks.data
    pin_input = form.transaction_pin.data
    user_id = session.get('user_id')

    db = get_db_connection()
    cursor = db.cursor()

    try:
      status = verify_pin(cursor, user_id, pin_input)
      
      if status == "ok":
        # Deduct only if enough balance
        cursor.execute("""
              UPDATE accounts
              SET balance = balance - %s
              WHERE user_id = %s AND balance >= %s
              """, (amount, user_id, amount))

        # 0 rows affected -> i.e balance < amount also handles the race condition
        if cursor.rowcount == 0:
          flash("Insufficient funds.", "danger")
          return render_template("deposit_withdraw.html", title="Withdraw", form=form, transaction_type="withdraw")

        # if balance >= amount and updaet query ran:
        cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
        account_id = cursor.fetchone()[0]

        cursor.execute("""
              INSERT INTO transactions 
              (amount, transaction_type, remarks, sender_acc_id) 
              VALUES 
              (%s, 'withdraw', %s, %s)""", (amount, remarks, account_id))

        db.commit()

        flash(f"Successfully withdrawn Rs {amount:,.2f} from your account.", "success")
        return redirect(url_for('main.dashboard'))
      
      else:
        db.commit()
        # this means that pin attempt failed
        if status == "locked":
          flash("Too many wrong attempts. Your account is locked for 15 minutes.", "danger")
      
        else:
           flash("Invalid transaction pin.", "danger")
          

    except Exception as e:
      db.rollback()
      flash("An unexpected database error occured. Please try again.", "danger")
      print(f"Withdraw error: {e}")

    finally:
      cursor.close()
      db.close()

  return render_template("deposit_withdraw.html", title="Withdraw", form=form, transaction_type="withdraw")

# TRANSFER VIA ACCOUNT NUMBER
@transactions.route("/transfer/account", methods=["GET", "POST"])
@is_logged_in
def transfer_account():
  form = AccountTransferForm(request.form)

  if request.method == "POST" and form.validate():
    account_num = form.account_number.data
    amount = form.amount.data
    remarks = form.remarks.data
    pin_input = form.transaction_pin.data
    user_id = session.get('user_id')

    db= get_db_connection()
    cursor = db.cursor()

    try:
      # Check if the enterred account number exists
      cursor.execute("SELECT account_num FROM accounts WHERE account_num = %s", (account_num,))
      result = cursor.fetchone()    # result -> Either None or A tuple of single value
  
      # if the entered account number exists
      if result:
        # Checking if the account number is user's own account number
        cursor.execute("SELECT account_num FROM accounts WHERE user_id = %s", (user_id,))
        sender_acc_num = cursor.fetchone()[0]

        if sender_acc_num == result[0]:
          flash("You can not transfer money to your own account.", "danger")
          return render_template("transfer_money.html", form=form, title="Transfer", transfer_type="account")
        
        status = verify_pin(cursor, user_id, pin_input)

        if status == "ok":
          cursor.execute("""
              UPDATE accounts
              SET balance = balance - %s
              WHERE user_id = %s AND balance >= %s
              """, (amount, user_id, amount))

          # 0 rows affected i.e. -> balance < aomunt .This check also handles race condition
          if cursor.rowcount == 0:
            flash("Insufficient funds.", "danger")
            return render_template("transfer_money.html", form=form, title="Transfer", transfer_type="account")

          cursor.execute("""
              UPDATE accounts
              SET balance = balance + %s
              WHERE account_num = %s
              """, (amount, account_num))

          # fetching sender account_id
          cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
          sender_acc_id = cursor.fetchone()[0]
          
          # Getting the account_id of the recipient
          cursor.execute("SELECT account_id FROM accounts WHERE account_num = %s", (account_num,))
          receiver_acc_id = cursor.fetchone()[0]

          cursor.execute("""
                INSERT INTO transactions 
                (amount, transaction_type, remarks, sender_acc_id, receiver_acc_id) 
                VALUES
                (%s, %s, %s, %s, %s)""", (amount, "transfer", remarks, sender_acc_id, receiver_acc_id))

          db.commit()

          flash(f"You have successfully transferred Rs {amount:,.2f}.", "success")
          return redirect(url_for("main.dashboard"))
        
        else:
          db.commit()
          if status == "locked":
            flash("Too many wrong attempts. Your account is locked for 15 minutes.", "danger")
          else:
            flash("Invalid transaction pin.", "danger")

      else:
        flash("Account number does not exist.", "danger")

    except Exception as e:
      db.rollback()
      flash("An unexpected error occured. Please try again later.", "danger")
      print(f"Transfer error: {e}")

    finally:
      cursor.close()
      db.close()

  return render_template("transfer_money.html", form=form, title="Transfer", transfer_type="account")

# TRANSFER VIA PHONE NUMBER
@transactions.route("/transfer/phone", methods=["GET", "POST"])
@is_logged_in
def transfer_phone():
  form = PhoneTransferForm(request.form)

  if request.method == "POST" and form.validate():
    phone_input = form.phone.data
    amount = form.amount.data
    remarks = form.remarks.data
    pin_input = form.transaction_pin.data
    user_id = session.get('user_id')

    db = get_db_connection()
    cursor = db.cursor()

    try:
      # Checking if the phone number exists
      cursor.execute("SELECT phone, user_id FROM users WHERE phone = %s", (phone_input,))
      result = cursor.fetchone()

      if result:
        # Checking if the enetered phone is the user's own 
        cursor.execute("SELECT phone FROM users WHERE user_id = %s", (user_id,))
        sender_phone_num = cursor.fetchone()[0]

        if sender_phone_num == result[0]:
          flash("You can not transfer money to your own account.", "danger")
          return render_template("transfer_money.html", form=form, title="Transfer", transfer_type="phone")

        status = verify_pin(cursor, user_id, pin_input)
        if status == "ok":
          cursor.execute("""
              UPDATE accounts
              SET balance = balance - %s 
              WHERE user_id = %s AND balance >= %s
              """, (amount, user_id, amount))

          # 0 rows affected i.e. -> balance < aomunt .This check also handles race condition
          if cursor.rowcount == 0:
            flash("Insufficient funds.", "danger")
            return render_template("transfer_money.html", form=form, title="Transfer", transfer_type="phone")
            
          cursor.execute("""
                UPDATE accounts
                SET balance = balance + %s
                WHERE user_id = %s
                """, (amount, result[1]))

          # fectch sender account_id
          cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id,))
          sender_acc_id = cursor.fetchone()[0]
          
          # Getting recipient account_id
          cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (result[1],))
          receiver_acc_id = cursor.fetchone()[0]

          cursor.execute("""
                INSERT INTO transactions
                (amount, transaction_type, remarks, sender_acc_id, receiver_acc_id)
                VALUES
                (%s, %s, %s, %s, %s)""", (amount, "transfer", remarks, sender_acc_id, receiver_acc_id))

          db.commit()

          flash(f"You have successfully transferred Rs {amount:,.2f}.", "success")
          return redirect(url_for("main.dashboard"))

        else:
          db.commit()
          if status == "locked":
            flash("Too many wrong attempts. Your account is locked for 15 minutes.", "danger")
          else:
           flash("Invalid transaction pin.", "danger")

      else:
        flash("Account does not exist.", "danger")

    except Exception as e:
      db.rollback()
      flash("An unexpected error occured. Please try again later.", "danger")
      print(f"Transfer error: {e}")

    finally:
      cursor.close()
      db.close()

  return render_template("transfer_money.html", form=form, title="Transfer", transfer_type="phone")

