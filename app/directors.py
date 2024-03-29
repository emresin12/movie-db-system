from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint, request, redirect, flash, url_for
from app.helper_functions import (
    create_director,
    create_user,
    define_director_platform,
    validate_date,
)
from pydantic import BaseModel, validator, Field
from functools import wraps
from .views import current_user


director_blueprint = Blueprint("director_blueprint", __name__)


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


@director_blueprint.route("/")
def directors_home_page():
    return render_template("DirectorsHome.html")



@director_blueprint.route("/list")
@login_required(role="Database_Manager")
def view_directors():
    query = """
    select d.username, u.name, u.surname, n.nation, dww.platform_id, rp.platform_name from directors d 
    join "User" u on d.username = u.username
    join nation n on d.nation_id = n.nation_id
    left join directorworkswith dww on dww.username = d.username
    left join ratingplatform rp on dww.platform_id = rp.platform_id
    """
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template(
        "TableView.html", fields=data[0], rows=data[1], table_title="Directors"
    )



@director_blueprint.route("/create")
@login_required(role="Database_Manager")
def create_director_page():
    nations = postgres_aws.get("SELECT * FROM nation")
    return render_template("DirectorsCreate.html", nations=nations)


class DirectorCreateRequestObject(BaseModel):
    username: str
    password: str
    name: str
    surname: str
    nation_id: int
    rating_platform_id: int = Field(default=None)

    def insert_to_database(self):
        create_user(
            username=self.username,
            password=self.password,
            name=self.name,
            surname=self.surname,
        )
        create_director(username=self.username, nation_id=self.nation_id)
        if self.rating_platform_id is not None:
            define_director_platform(
                username=self.username, platform_id=self.rating_platform_id
            )
        return True

    @validator("nation_id")
    def validate_nation_id(cls, nation_id):
        # Perform the query to check if the nation_id exists in the table
        query = f"SELECT * FROM nation WHERE nation_id = {nation_id}"
        result = postgres_aws.get(query)

        if not result:
            raise ValueError(f"Nation with ID {nation_id} does not exist.")

        return nation_id

    @validator("rating_platform_id")
    def validate_rating_platform_id(cls, rating_platform_id):
        if rating_platform_id is None:
            return None
        # Perform the query to check if the nation_id exists in the table
        query = f"SELECT * FROM ratingplatform WHERE platform_id = {rating_platform_id}"
        result = postgres_aws.get(query)

        if not result:
            raise ValueError(
                f"Rating Platform with ID {rating_platform_id} does not exist."
            )

        return rating_platform_id



@director_blueprint.route("/create_submit", methods=["POST"])
@login_required(role="Database_Manager")
def submit():
    if request.method == "POST":
        # Access the form data
        data = {**request.form}
        try:
            if data["rating_platform_id"] == "":
                data["rating_platform_id"] = None
            obj = DirectorCreateRequestObject(**data)
            obj.insert_to_database()
        except Exception as e:
            flash(str(e.args), "error")
            return redirect(url_for("director_blueprint.create_director_page"))
    flash("Director is created successfully!", "success")
    return redirect(url_for("director_blueprint.create_director_page"))


@director_blueprint.route("/available_theatres", methods=["POST", "GET"])
@login_required(role="Director")
def listTheathersForSlot():
    if request.method == "POST":
        slot = request.form.get("slot")
        date = request.form.get("date")

        if validate_date(date):
            query = f"""select * from Theatre t where t.theatre_id not in (select m.theatre_id from moviesession m where m.time_slot = '{slot}' and m.date = '{date}')"""
            ret = postgres_aws.get_rows_and_fields_from_sql(query)
            return render_template(
                "TableView.html", fields=ret[0], rows=ret[1], table_title="Theaters"
            )
        else:
            flash("Date is not valid!", "error")
            return
    # I want to select the theaters that are not available in movie sessions table
    else:
        return render_template("DirectorAvailableTheatre.html")


@director_blueprint.route("/update_movie_name", methods=["POST", "GET"])
@login_required(role="Director")
def updateMovieName():
    # Directors will update a movie by movie id and new movie name. But the movie has to be the one that they directed.
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        new_movie_name = request.form.get("name")
        username = current_user.get_id()
        query = f"""select * from Movie m where m.movie_id = {movie_id} and m.director_username = '{username}'"""
        ret = postgres_aws.get(query)
        if ret:
            query = f"""update Movie set movie_name = '{new_movie_name}' where movie_id = {movie_id}"""
            postgres_aws.write(query)

            return render_template(
                "DirectorUpdateMovieName.html",
                error="Movie name is updated successfully!",
            )
        else:

            return render_template(
                "DirectorUpdateMovieName.html",
                error="There is no such movie ID of for this director!",
            )
    else:
        return render_template("DirectorUpdateMovieName.html")



@director_blueprint.route("/update_platform")
@login_required(role="Database_Manager")
def update_platform_page():
    rating_platforms = postgres_aws.get("SELECT * FROM nation")
    return render_template(
        "DirectorsUpdateRatingPlatform.html", platforms=rating_platforms
    )



@director_blueprint.route("/update_platform_id", methods=["POST"])
@login_required(role="Database_Manager")
def update_platform():
    if request.method == "POST":
        # Access the form data
        data = request.form
        # check if username exists
        exists = postgres_aws.get(
            f"select * from directors where username = '{data['username']}' "
        )
        if not exists:
            flash("Director does not exist", "error")
            return redirect(url_for("director_blueprint.update_platform_page"))
        # check if rating platform exists
        exists = postgres_aws.get(
            f"select * from ratingplatform where platform_id = {data['rating_platform_id']} "
        )
        if not exists:
            flash("Rating Platform does not exist", "error")
            return redirect(url_for("director_blueprint.update_platform_page"))
        # check if rating platform exists for director
        exists = postgres_aws.get(
            f"select * from directorworkswith where username = '{data['username']}' "
        )
        if exists:
            # overwrite director's rating platform
            postgres_aws.write(
                f"update directorworkswith set platform_id = {data['rating_platform_id']} where username = '{data['username']}' "
            )
        else:
            # create director's rating platform
            postgres_aws.write(
                f"insert into directorworkswith (username, platform_id) values ('{data['username']}', {data['rating_platform_id']})"
            )
    flash("Director's platform id is updated successfully!", "success")
    return redirect(url_for("director_blueprint.update_platform_page"))
