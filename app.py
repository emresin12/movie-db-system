import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask(__name__)


@app.route('/')
def hello_world():
    return os.environ.get('POSTGRES_PASSWORD')


@app.route('/get_from_db')
def db_test():
    from clients.postgres.postgresql_db import postgres_aws
    query = 'SELECT * FROM history'
    response = postgres_aws.get(query)
    return str(response)


@app.route('/insert_to_db')
def db_insert_test():
    from clients.postgres.postgresql_db import postgres_aws
    query = """INSERT INTO history (author, title, type, year)
    VALUES ('Halis', 'Test1', 'Test', '1961');"""

    response = postgres_aws.write(query)
    return str(response)


if __name__=='__main__':
    app.run()
