from dotenv import load_dotenv

from app.audience import audience_blueprint
from clients.postgres.postgresql_db import postgres_aws
from flask import Flask, request, render_template, redirect, session,url_for
import os
from functools import wraps

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)


#load_dotenv()
app = Flask(__name__)
from app.crud_table import crud_table_blueprint
from app.directors import director_blueprint

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.secret_key = os.environ.get("SECRET_KEY")


#id of the user class is username of the system
class User(UserMixin):
    def __init__(self, user):
       
        self.id = user[0]["username"]
        self.password = user[0]["password"]
        self.urole=user[0]["user_role"]

    def get_id(self):
        return self.id
    def get_urole(self):
        return self.urole




@login_manager.user_loader
def load_user(user_id):
    query = f"""select sub.username                          as username,
       sub.password                          as password,
       (case
            when (select count(*) > 0 from audience where sub.username = audience.username) then 'Audience'
            when (select count(*) > 0 from directors where sub.username = directors.username) then 'Director'
            when (select count(*) > 0 from databasemanagers where sub.username = databasemanagers.username)
                then 'Database_Manager' end) as user_role
        from (select u.username, u.password
            from "User" u
            union all
            select dm.username, dm.password
            from databasemanagers dm) sub
        where sub.username = '{user_id}'
        """
    user = postgres_aws.get(query)
    print("loadtan çağrı")
    print(user,user_id)

    if user:
        print(True)
        print("loadtan çağrı")
        print(user)
        return User(user)
    else:
        print(False)
        print("loadtan çağrı")
        return None

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if not current_user.is_authenticated:
               return app.login_manager.unauthorized()
            urole = current_user._get_current_object().get_urole()
            print(urole)
            if ( (urole != role) and (role != "ANY")):
                return render_template("index.html",error ="not authorized")   
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


@app.route("/")
@login_required("ANY")
def index():
    print("indexten")
    print(current_user.is_authenticated)
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the PostgreSQL database
       
        # Check if the user exists in the database
        query = f"""select sub.username                          as username,
       sub.password                          as password,
       (case
            when (select count(*) > 0 from audience where sub.username = audience.username) then 'Audience'
            when (select count(*) > 0 from directors where sub.username = directors.username) then 'Director'
            when (select count(*) > 0 from databasemanagers where sub.username = databasemanagers.username)
                then 'Database_Manager' end) as user_role
from (select u.username, u.password
      from "User" u
      union all
      select dm.username, dm.password
      from databasemanagers dm) sub
where sub.username = '{username}'
  and sub.password = '{password}'"""
        user = postgres_aws.get(query)
        print(user)
        if user:
     
            userObj = User(user)
            login_user(userObj)
            print(current_user.is_authenticated)
            print(current_user.get_id())
            
            next = request.args.get('next')
            print(next)
    
            return redirect(next or url_for('index'))
        else:
            # Invalid credentials
            error = "Invalid username or password"
            return render_template("login.html", error=error)
    return render_template("login.html")
@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return "goodbye"



app.register_blueprint(crud_table_blueprint)
app.register_blueprint(director_blueprint)
app.register_blueprint(audience_blueprint)

app.run()
