from wtforms import DecimalField, StringField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Regexp, ValidationError
from flask_wtf import FlaskForm
import re              # Python's regular expression module.


# CREATING A CUSTOM VALIDATOR TO ACCEPT AMOUNT TO 2 DECIMAL PLACES
def max_two_decimal_places(form, field):
  if not field.raw_data:
    return
  
  raw = field.raw_data[0].strip()
  if not re.match(r'^\d+(\.\d{1,2})?$', raw):
    raise ValidationError("Amount can have at most 2 decimal places.")


# Form for Deposit and Withdraw
class TransactionForm(FlaskForm):
  amount = DecimalField(
    "Amount",
    validators=[DataRequired(message="Please enter an amount."),
                NumberRange(min=10, max=100000 ,message="Amount must be between Rs 10 and Rs 100000."),
                max_two_decimal_places],
    places=2
  )
  remarks = StringField(
    "Remarks",
    validators=[DataRequired(message="Please enter your remarks."),
                Length(min=3, max=100, message=("Remarks must be between 3 and 100 characters."))]
  )

  transaction_pin = PasswordField(
      "Transction Pin",
      validators=[DataRequired(),
                  Length(min=4, max=4, message="Pin must be of 4 digits."),
                  Regexp(r'^\d{4}$', message="Invalid transaction pin.")]
  )


# Form for transfer via account number by inheriting the base class
class AccountTransferForm(TransactionForm):
  account_number = StringField(
      "Receiver's Account Number",
      validators=[DataRequired(),
                  Regexp(r'^\d{16}$', message="Account number must be exactly 16 digits.")]
  )

# Form for transfer via phone number
class PhoneTransferForm(TransactionForm):
  phone = StringField(
      "Receiver's Phone Number",
      validators=[DataRequired(),
                  Regexp(r'^9[78]\d{8}$', message="Invalid phone number.")]
)