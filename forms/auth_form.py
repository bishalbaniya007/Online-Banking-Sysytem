from wtforms import  StringField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, Email, EqualTo
from flask_wtf import FlaskForm

# Registration Form
class RegisterForm(FlaskForm):
  first_name = StringField(
    "First Name",
    validators=[DataRequired(), 
                Length(max=50, message="Length can not exceed 50."),
                Regexp(r'^[a-zA-Z\s\-]+$', message="Name can only contain letters, spaces, and hyphens.")]
  )

  last_name = StringField(
    "Last Name",
    validators=[DataRequired(), 
                Length(max=50, message="Length can not exceed 50."),
                Regexp(r'^[a-zA-Z\s\-]+$', message="Name can only contain letters, spaces, and hyphens.")]
  )

  username = StringField(
    "Username",
    validators=[DataRequired(),
                Length(max=50, message="Length can not exceed 50."),
                Regexp(r'^[a-zA-Z0-9_]+$', message="Username can only contain letters, numbers, and underscores.")
                ]
  )

  email = StringField(
    "Email address",
    validators=[DataRequired(),
                Email(message="Invalid email format."),
                Length(max=50, message="Email lenght can not exceed 50.")]
  )

  phone = StringField(
    "Phone Number",
    validators=[DataRequired(),
                Length(min=10, max=10, message="Phone number must be of 10 digits."),
                Regexp(r'^9[78]\d{8}$', message="Invalid phone number.")]
  )

  password = PasswordField(
    "Password",
    validators=[DataRequired(),
                Length(min=8, max=64, message="Password must be between 8 and 64 characters."),
                Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&#_+-]).+$', 
                       message="Password must contain at least one letter, one special character and one number."),
                EqualTo("confirm_password", message="Password do not match.")]
  )

  confirm_password = PasswordField(
    "Confirm Password",
    validators=[DataRequired()]
  )

  transaction_pin = PasswordField(
    "Transction Pin",
    validators=[DataRequired(),
                Length(min=4, max=4, message="Pin must be of 4 digits."),
                Regexp(r'^\d{4}$', message="Invalid transaction pin.")]
  )

# Login Form
class LoginForm(FlaskForm):
  phone = StringField(
    "Phone number",
    validators=[DataRequired(message="Please enter your login credential.")]
  )

  password = PasswordField(
    "Password",
    validators=[DataRequired(message="Please enter your login password.")]
  )