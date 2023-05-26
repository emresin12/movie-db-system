# 2. Database managers shall be able to add new Users (Audiences or Directors)
# to the system.
from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint, request, redirect, flash, url_for
from app.helper_functions import create_audience, create_user, define_director_platform
from pydantic import BaseModel
from functools import wraps
from .views import current_user

audience_blueprint = Blueprint("audience_blueprint", __name__)


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return render_template(
                    "login.html"
                )  # this should be the right method to call unauthorized view
            urole = current_user._get_current_object().get_urole()
            print(urole)
            if (urole != role) and (role != "ANY"):
                return render_template("index.html", error="not authorized")
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


@audience_blueprint.route("/audience")
def directors_home_page():
    return render_template("AudienceHome.html")


@audience_blueprint.route("/audience/list")
def view_audience():
    query = """
    select u.username, u.name, u.surname from audience a 
    join "User" u on a.username = u.username
    """
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template(
        "TableView.html", fields=data[0], rows=data[1], table_title="Audience"
    )


@audience_blueprint.route("/audience/create")
def create_audience_page():
    return render_template("AudienceCreate.html")


class AudienceCreateRequestObject(BaseModel):
    username: str
    password: str
    name: str
    surname: str

    def insert_to_database(self):
        create_user(
            username=self.username,
            password=self.password,
            name=self.name,
            surname=self.surname,
        )
        create_audience(username=self.username)
        return True


@audience_blueprint.route("/audience/create_submit", methods=["POST"])
def submit():
    if request.method == "POST":
        # Access the form data
        data = request.form
        try:
            obj = AudienceCreateRequestObject(**data)
            obj.insert_to_database()
        except Exception as e:
            flash(str(e.args), "error")
            return redirect(url_for("audience_blueprint.create_audience_page"))
    flash("Audience is created successfully!", "success")
    return redirect(url_for("audience_blueprint.create_audience_page"))

@audience_blueprint.route("/audience/delete", methods=["POST","GET"])
def delete_audience():
    if request.method == "POST":
        data = request.form
        username = data["username"]

        res = postgres_aws.get(f"""select * from Audience where username = '{username}'""") # check if it is an audience 
        if len(res) == 0:
            flash("User is not an audience!", "error")
            return redirect(url_for("audience_blueprint.delete_audience"))
        query = f"""
        delete from "User" where username = '{username}'
        """
        postgres_aws.write(query)
        return redirect(url_for("audience_blueprint.view_audience"))
    
    return render_template("DeleteAudienceByManager.html")