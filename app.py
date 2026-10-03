from flask import Flask
from flask_wtf import CSRFProtect
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

csrf = CSRFProtect(app)   # protects from malicious attacks

from routes.main import main
from routes.auth import auth
from routes.transactions import transactions
from routes.settings import settings

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(transactions)
app.register_blueprint(settings)

if __name__ == "__main__":
  app.run(debug=True)
 