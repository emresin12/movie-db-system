from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)



login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()


from app.crud_table import crud_table_blueprint

load_dotenv()

app = Flask(__name__)

#initialize for the login system
login_manager.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)

@app.route('/')
def hello_world():
    return "hello world"


app.register_blueprint(crud_table_blueprint)
app.run()
