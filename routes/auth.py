from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from forms.auth_form import RegisterForm, LoginForm
from passlib.hash import sha256_crypt
from database import get_db_connection
import random
from utils.decorators import is_logged_in
from utils.security import verify_password

auth = Blueprint("auth", __name__)

# generating unique 16-digits account number randomly for users
def generate_account_number(cursor):
  while True:
    account_num = str(random.randint(10**15, 10**16 - 1))

    cursor.execute("SELECT account_id FROM accounts WHERE account_num = %s", (account_num,))

    # returning the unique account_num
    if not cursor.fetchone():
      return account_num


# Registration
@auth.route("/register", methods=["GET", "POST"])
def register():
  form = RegisterForm(request.form)

  if request.method == "POST" and form.validate():
    # 1. Storing the data from form
    first_name = form.first_name.data
    last_name = form.last_name.data
    username = form.username.data
    email = form.email.data
    password = sha256_crypt.encrypt(str(form.password.data))
    transaction_pin = sha256_crypt.encrypt(str(form.transaction_pin.data))
    phone = form.phone.data

    # establishing db connection
    db = get_db_connection()

    # creating a cursor
    cursor = db.cursor()
          
    try:
      # 2. Cheking if username or email or phone number is already taken
      cursor.execute("SELECT username, email, phone FROM users WHERE username = %s OR email = %s OR phone = %s", (username, email, phone))
  
      # storing the first row of the match from select query
      existing_user = cursor.fetchone()   # fecthone() -> returns either a tuple of (username, email, phone) or None
  
      # 3. Returning the specific error to the user
      if existing_user:
        db_username, db_email, db_phone = existing_user
        # checking for match individually
        if db_username == username:
          flash("Username is already taken.", "danger")
        elif db_email == email:
          flash("Email is already registered.", "danger")
        elif db_phone == phone:
          flash("Phone number is already registered.", "danger")

        return render_template("register.html", form=form, title="Register")
        

      # 4. If no match is found
      # Inserting the values in users table
      cursor.execute("INSERT INTO users (first_name, last_name, username, email, password, transaction_pin, phone) VALUES (%s, %s, %s, %s, %s, %s, %s)", (first_name, last_name, username, email, password, transaction_pin, phone))

      # 4. Generating and inserting the 16-digits account number
      # Captures the unique ID number that MySQL automatically generated for the person we just registered.
      new_user_id = cursor.lastrowid    # buil-in attribute that retrives the last row_id  
      account_num = generate_account_number(cursor)
      cursor.execute("INSERT INTO accounts (account_num, user_id) VALUES (%s, %s)", (account_num, new_user_id))

      # commiting the query
      db.commit()
      flash("You have been registered successfully.", "success")
      # redirecting to login page
      return redirect(url_for("auth.login"))

    except Exception as e:
      db.rollback()   # undo all commited changes
      flash("An unexpected database error occurred. Please try again.", "danger")
      print(f"Database error: {e}")   # for me to see the database error in terminal
      return render_template("register.html", title="Register", form=form)

    finally:
      cursor.close()      # closing cursor
      db.close()          # closing the database connection

    

  return render_template("register.html", title="Register", form=form)


# Login 
@auth.route("/", methods=["GET", "POST"])
@auth.route("/login", methods=["GET", "POST"])
def login():
  form = LoginForm(request.form)

  if request.method == "POST" and form.validate():
    phone_input = form.phone.data
    password_input = form.password.data

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
      # checking if the phone number exists in our database
      cursor.execute("SELECT * FROM users WHERE phone = %s", (phone_input,))

      # stores the first row of the result from query
      user = cursor.fetchone()

      # if user exists
      if user:
        user_id = user["user_id"]
        status = verify_password(cursor, user_id, password_input)
        db.commit()   # saves the counter on every outcome

        if status == "ok":
          session.clear()
          session["logged_in"] = True
          session["user_id"] = user_id
          session["first_name"] = user["first_name"]
          session["last_name"] = user["last_name"]
          session["username"] = user["username"]
          session["phone"] = user["phone"]

          flash("You have logged in successfully.", "success")
          return redirect(url_for("main.dashboard"))

        if status == "locked":
          flash("Too many wrong attempts. Your account is locked for 15 minutes.", "danger")
          return render_template("login.html", title="Login", form=form)

      # passwords do not match or user does not exist
      flash("Invalid phone number or password.", "danger")
      

    except Exception as e:
      flash("An unexpected error occured. Please try again.", "danger")
      print(f"Login error. {e}")

    finally:
      cursor.close()
      db.close()

  return render_template("login.html", title="Login", form=form)


# Logout
@auth.route("/logout", methods=["POST"])
@is_logged_in
def logout():
  session.clear()
  flash("You have been logged out.", "success")
  return redirect(url_for("auth.login"))