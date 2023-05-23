from dotenv import load_dotenv
from flask import Flask

from app.crud_table import crud_table_blueprint
from app.directors import director_blueprint

load_dotenv()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "hello world"


app.register_blueprint(crud_table_blueprint)
app.register_blueprint(director_blueprint)

app.run()
