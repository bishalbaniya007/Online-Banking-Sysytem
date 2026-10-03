from flask import Blueprint, render_template, request, redirect, flash, session, url_for, abort
from utils.decorators import is_logged_in
from forms.settings_form import ChangePassword, ChangePin, UpdateProfile
from database import get_db_connection
from passlib.hash import sha256_crypt
from utils.security import verify_pin, verify_password

settings = Blueprint("settings", __name__)

@settings.route("/settings/change_password", methods=["GET", "POST"])
@is_logged_in
def change_password():
  form = ChangePassword(request.form)

  if request.method == "POST" and form.validate():
    current_password = form.current_password.data
    new_password = form.new_password.data
    user_id = session.get('user_id')

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
      status = verify_password(cursor, user_id, current_password)

      if status == "ok":
        if new_password == current_password:
          flash("New password must be different from your current password.", "danger")
          return render_template("change_password.html", title="Change Password", form=form)

        # if different:
        new_password = sha256_crypt.encrypt(new_password)
        
        cursor.execute("""
              UPDATE users
              SET password = %s
              WHERE user_id = %s""", (new_password, user_id))

        db.commit()

        flash("Password updated successfully.", "success")
        return redirect(url_for("main.settings"))

      else:
        db.commit()
        if status == "locked":
          flash("Too many wrong attempts. Your accounts is locked for 15 minutes.", "danger")
        else:
          flash("Invalid password.", "danger")

    except Exception as e:
      db.rollback()
      flash("An unexpected error occured. Please try again.", "danger")
      print(f"Change password error: {e}")

    finally:
      cursor.close()
      db.close()

  return render_template("change_password.html", title="Change Password", form=form)

@settings.route("/settings/change_pin", methods=["GET", "POST"])
@is_logged_in
def change_pin():
  form = ChangePin(request.form)

  if request.method == "POST" and form.validate():
    current_pin = form.current_pin.data
    new_pin = form.new_transaction_pin.data
    user_id = session.get('user_id')

    db = get_db_connection()
    cursor = db.cursor()

    try:
      status = verify_pin(cursor, user_id, current_pin)

      if status == "ok":
        # checking if the current pin and new pin are same
        if new_pin == current_pin:
          flash("New pin must be different from your current pin.", "danger")
          return render_template("change_pin.html", title="Change Pin", form=form)

        # if different:
        new_pin = sha256_crypt.encrypt(str(new_pin))

        cursor.execute("""
              UPDATE users
              SET transaction_pin = %s
              WHERE user_id = %s """, (new_pin, user_id))

        db.commit()

        flash("Transaction Pin updated successfully.", "success")
        return redirect(url_for("main.settings"))

      else:
        db.commit()
        if status == "locked":
          flash("Too many wrong attempts. Your account is locked for 15 minutes.", "danger")
        else:
          flash("Invalid transaction pin.", "danger")
          
    except Exception as e:
      db.rollback()
      flash("An unexpected error occured. Please try again.", "danger")
      print(f"Change pin error: {e}")

    finally:
      cursor.close()
      db.close()

  return render_template("change_pin.html", title="Change Pin", form=form)

@settings.route("/settings/account_details")
@is_logged_in
def account_details():
  user_id = session.get('user_id')

  db = get_db_connection()
  cursor = db.cursor(dictionary=True)

  result = None
  try:
    cursor.execute("""
          SELECT u.first_name, u.last_name, u.username, u.email, u.phone, a.account_num, a.balance
          FROM users u
          INNER JOIN accounts a ON a.user_id = u.user_id
          WHERE u.user_id = %s""", (user_id,))

    result = cursor.fetchone()

  except Exception as e:
    flash("An unexpected error occured. Please try again.", "danger")
    print(f"Error: {e}")
    
  finally:
    cursor.close()
    db.close()

  return render_template("account_details.html", title="My Account", account=result)


# UPDATE PROFILE 
@settings.route("/settings/update_profile/<int:user_id>", methods=["POST", "GET"])
@is_logged_in
def update_profile(user_id):
  
  # checking if the passed user_id is of the user or not
  if session.get('user_id') != user_id:
    abort(403)

  form = UpdateProfile(request.form)

  db =get_db_connection()
  cursor = db.cursor()

  try:
    cursor.execute("""
          SELECT * FROM users WHERE user_id = %s""", (user_id,))

    result = cursor.fetchone()
    if not result:
      flash("User does not exist.", "danger")
      return redirect(url_for("main.settings"))

    # Now that user Exists
    # fetching the info
    cursor.execute("""
        SELECT first_name, last_name, username, email, phone 
        FROM users
        WHERE user_id = %s""", (user_id,))

    first_name, last_name, username, email, phone = cursor.fetchone()

    # filling the form for get request
    if request.method == "GET":
      form.first_name.data = first_name
      form.last_name.data = last_name
      form.username.data = username
      form.email.data = email
      form.phone.data = phone

    if request.method == "POST" and form.validate():
      first_name = form.first_name.data
      last_name = form.last_name.data
      username = form.username.data
      email = form.email.data
      phone = form.phone.data

      # checking if email or phone is already taken
      cursor.execute("""
            SELECT username, email, phone FROM users
            WHERE (username = %s OR email = %s OR phone = %s) AND user_id != %s
            """, (username, email, phone, user_id))
      result = cursor.fetchone()
    
      if result:
        db_username, db_email, db_phone = result
        if db_username == username:
          flash("Username already taken.", "danger")
        elif db_email == email:
          flash("Email already taken.", "danger")
        elif db_phone == phone:
          flash("Phone number already taken.", "danger")

        return render_template("update_profile.html", form=form)

      # now that all username email and phone is available
      cursor.execute("""
            UPDATE users
            SET first_name = %s,
                last_name = %s,
                username = %s,
                email = %s,
                phone= %s
            WHERE user_id = %s""", (first_name, last_name, username, email, phone, user_id))

      # updating the data stored in session
      session["logged_in"] = True
      session["first_name"] = first_name
      session["last_name"] = last_name
      session["username"] = username
      session["phone"] = phone

      db.commit()
      flash("Details updated successfully.", "success")
      return redirect(url_for("main.settings"))
      
  except Exception as e:
    db.rollback()
    flash("An unexpected error occured. Please try again.", "danger")
    print(f"Update Profile Error: {e}")

  finally:
    cursor.close()
    db.close()

  return render_template("update_profile.html", form=form)



