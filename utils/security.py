from datetime import datetime, timedelta
from passlib.hash import sha256_crypt

MAX_ATTEMPTS = 5
LOCK_MINUTES = 15

# Returns 'ok', 'wrong' or 'locked'.
def verify_pin(cursor, user_id, pin_input):
  cursor.execute("""
        SELECT transaction_pin, failed_pin_attempts, pin_locked_until
        FROM users 
        WHERE user_id = %s FOR UPDATE""", (user_id,))
  pin_hash, attempts, locked_until = cursor.fetchone()

  # checking if the account is locked 
  if locked_until and locked_until > datetime.now():
    return "locked"

  # verifying password
  if sha256_crypt.verify(pin_input, pin_hash):
    # if the account isnot locked, and user enters correct password
    cursor.execute("""
          UPDATE users 
          SET failed_pin_attempts = 0, 
              pin_locked_until = NULL
          WHERE user_id = %s""", (user_id,))
    return "ok"

  # Wrong password
  attempts += 1
  if attempts >= MAX_ATTEMPTS:    # max attempts reached then locking the account
    lock_until = datetime.now() + timedelta(minutes=LOCK_MINUTES)

    cursor.execute("""
          UPDATE users 
          SET failed_pin_attempts = 0, 
              pin_locked_until = %s
          WHERE user_id = %s""", (lock_until, user_id))
    
  # max attempts not reached so updating attempts in database
  else:   
    cursor.execute("UPDATE users SET failed_pin_attempts = %s WHERE user_id = %s",
                   (attempts, user_id))
    
  return "wrong"


# this function is to verify password
def verify_password(cursor, user_id, password_input):
  # login uses -> cursor = db.cursor(dictionary=True)
  cursor.execute("""
        SELECT password, failed_password_attempts, password_locked_until
        FROM users 
        WHERE user_id = %s FOR UPDATE""", (user_id,))
  
  row = cursor.fetchone()
  password_hash = row["password"]
  attempts = row["failed_password_attempts"]
  lock_until = row["password_locked_until"]

  if lock_until and lock_until > datetime.now():
    return "locked"

  if sha256_crypt.verify(password_input, password_hash):
    cursor.execute("""
          UPDATE users
          SET failed_password_attempts = 0,
              password_locked_until = NULL
          WHERE user_id = %s""", (user_id,))
    return "ok"

  attempts += 1
  if attempts >= MAX_ATTEMPTS:
    lock_until = datetime.now() + timedelta(minutes=LOCK_MINUTES)

    cursor.execute("""
          UPDATE users 
          SET failed_password_attempts = 0, 
              password_locked_until = %s
          WHERE user_id = %s""", (lock_until, user_id))
    
  # max attempts not reached so updating attempts in database
  else:   
    cursor.execute("UPDATE users SET failed_password_attempts = %s WHERE user_id = %s",
                    (attempts, user_id))
    
  return "wrong"