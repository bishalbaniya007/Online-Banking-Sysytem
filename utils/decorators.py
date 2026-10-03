from functools import wraps
from flask import session, flash, redirect, url_for

# check if user is logged_in
def is_logged_in(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if session.get('logged_in'):
      return f(*args, **kwargs)
    else:
      flash("Unauthorized access. Please Login.", "danger")
      return redirect(url_for("auth.login"))
  return wrap