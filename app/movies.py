from flask_login import current_user
from app.helper_functions import get_predecessors
from clients.postgres.postgresql_db import postgres_aws

from flask import render_template, Blueprint, request, flash
from functools import wraps
from .views import current_user
from pydantic import BaseModel, validator


movies_blueprint = Blueprint("movies_blueprint", __name__)


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


@movies_blueprint.route("/")
def view_movies_home_page():

    return render_template("MoviesHome.html")


class CreateMovieRequest(BaseModel):
    movie_id: int
    movie_name: str
    duration: int
    genre_list: list

    def insert_into_database(self):
        director_username = current_user.get_id()

        query = f"insert into movie (movie_id, movie_name, duration, director_username) values ({self.movie_id}, '{self.movie_name}', {self.duration}, '{director_username}')"
        postgres_aws.write(query)

        for genre in self.genre_list:
            query = f"insert into moviegenres (movie_id, genre_id) values ({self.movie_id}, {genre})"
            postgres_aws.write(query)

        return True


@movies_blueprint.route("/create_movie", methods=["GET", "POST"])
def create_movie():
    query = "select * from genre"
    genres = postgres_aws.get(query)
    if request.method == "GET":
        return render_template("MoviesCreate.html", genres=genres)
    elif request.method == "POST":
        input_request = {
            "movie_id": request.form["movie_id"],
            "movie_name": request.form["movie_name"],
            "duration": request.form["duration"],
            "genre_list": request.form.getlist("genre_list"),
        }
        try:
            data = CreateMovieRequest(**input_request)
            data.insert_into_database()
            flash("Movie created successfully!")
            return render_template("MoviesCreate.html", genres=genres)
        except Exception as e:
            flash(str(e))
            return render_template("MoviesCreate.html", genres=genres, error=e)


class CreateMovieSessionRequest(BaseModel):
    movie_id: int
    theatre_id: int
    time_slot: int
    input_date: str

    def insert_to_database(self):
        # get max session_id
        max_session_id = postgres_aws.get(
            "select max(session_id) as max_session_id from moviesession"
        )[0]["max_session_id"]
        query = f"insert into moviesession (session_id, movie_id, theatre_id, time_slot, date) values ({max_session_id+1}, {self.movie_id}, {self.theatre_id}, {self.time_slot}, '{self.input_date}')"
        postgres_aws.write(query)
        return True


@movies_blueprint.route("/create_session", methods=["GET", "POST"])
def create_movie_session():
    query = "select movie_id, movie_name from movie"
    movies = postgres_aws.get(query)
    query = "select theatre_id, theatre_name from theatre"
    theatres = postgres_aws.get(query)
    if request.method == "GET":
        return render_template(
            "MoviesSessionCreate.html", movies=movies, theatres=theatres
        )
    elif request.method == "POST":
        try:
            print(request.form)
            data = CreateMovieSessionRequest(**request.form)
            data.insert_to_database()
            flash("Movie Session created successfully!")
            return render_template(
                "MoviesSessionCreate.html", movies=movies, theatres=theatres
            )
        except Exception as e:
            flash(str(e))
            return render_template(
                "MoviesSessionCreate.html", movies=movies, theatres=theatres, error=e
            )


class AddPredecessorsRequest(BaseModel):
    movie_id: int
    predecessor_list: list

    def insert_into_database(self):
        for predecessor in self.predecessor_list:
            query = f"insert into moviepredecessors (followup_movie_id, predecessor_movie_id) values ({self.movie_id}, {predecessor})"
            postgres_aws.write(query)
        return True


@movies_blueprint.route("/add_predecessors", methods=["GET", "POST"])
def add_predecessors():
    query = "select * from movie"
    movies = postgres_aws.get(query)
    if request.method == "GET":
        return render_template("MoviesAddPredecessor.html", movies=movies)
    elif request.method == "POST":
        input_request = {
            "movie_id": request.form["movie_id"],
            "predecessor_list": request.form.getlist("predecessor_list"),
        }
        try:
            data = AddPredecessorsRequest(**input_request)
            print(data.dict())
            data.insert_into_database()
            flash("Predecessors are set successfully!")
            return render_template("MoviesAddPredecessor.html", movies=movies)
        except Exception as e:
            flash(str(e))
            return render_template("MoviesAddPredecessor.html", movies=movies, error=e)


@movies_blueprint.route("/movies_by_director")
def get_movies_by_director():
    query = f"select m.movie_id, m.movie_name, (select ms.theatre_id from moviesession ms where ms.movie_id = m.movie_id) as theatre_id, (select ms.time_slot from moviesession ms where ms.movie_id = m.movie_id)  as time_slot from movie m where m.director_username = '{current_user.get_id()}'"
    movie_data = postgres_aws.get(query)
    if not movie_data:
        return render_template(
            "MoviesByCurrentDirector.html", table_title="No Movie Found"
        )
    output = []
    for movie in movie_data:
        temp_data = movie
        movie_id = temp_data["movie_id"]
        temp_data["predecessors_list"] = get_predecessors(movie_id)
        output.append(temp_data)
    converted_rows = [
        [
            d["movie_id"],
            d["movie_name"],
            d["theatre_id"],
            d["time_slot"],
            ", ".join([str(x) for x in d["predecessors_list"] if x != ""]),
        ]
        for d in output
    ]
    return render_template(
        "MoviesByCurrentDirector.html",
        fields=[
            "movie_id",
            "movie_name",
            "theatre_id",
            "time_slot",
            "predecessors_list",
        ],
        rows=converted_rows,
        table_title="Movies by Current Director (You)",
    )


movies_ratings_blueprint = Blueprint("movies_ratings_blueprint", __name__)
movies_blueprint.register_blueprint(movies_ratings_blueprint, url_prefix="/ratings")


@movies_ratings_blueprint.route("/")
def view_ratings_by_audience():
    return render_template(
        "MoviesViewRatingsByAudience.html", fields=[], rows=[], table_title=""
    )


@movies_ratings_blueprint.route("/results", methods=["POST"])
def results():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        query = f"select m.movie_id, m.movie_name, ratings.rating from ratings join movie m on ratings.movie_id = m.movie_id where username = '{username}'"
        data = postgres_aws.get_rows_and_fields_from_sql(query)
        if not data:
            return render_template(
                "MoviesViewRatingsByAudience.html",
                fields=[],
                rows=[],
                table_title=f"No ratings for {username}",
            )
        return render_template(
            "MoviesViewRatingsByAudience.html",
            fields=data[0],
            rows=data[1],
            table_title=f"Movie Ratings for {username}",
        )


movies_by_director_blueprint = Blueprint("movies_by_director_blueprint", __name__)
movies_blueprint.register_blueprint(
    movies_by_director_blueprint, url_prefix="/by_director"
)


@movies_by_director_blueprint.route("/")
def view_movies_by_director():
    return render_template("MoviesByDirector.html", fields=[], rows=[], table_title="")


@movies_by_director_blueprint.route("/results", methods=["POST"])
def results_by_director():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        query = f"select m.movie_id, m.movie_name, (select t.theatre_id from moviesession ms join theatre t on ms.theatre_id = t.theatre_id where ms.movie_id = m.movie_id limit 1) as theatre_id, (select t.theatre_district from moviesession ms join theatre t on ms.theatre_id = t.theatre_id where ms.movie_id = m.movie_id limit 1) as district, (select ms.time_slot from moviesession ms join theatre t on ms.theatre_id = t.theatre_id where ms.movie_id = m.movie_id limit 1) as time_slot from movie m where m.director_username = '{username}'"
        data = postgres_aws.get_rows_and_fields_from_sql(query)
        if not data:
            return render_template(
                "MoviesByDirector.html",
                fields=[],
                rows=[],
                table_title=f"No movies for {username}",
            )
        return render_template(
            "MoviesByDirector.html",
            fields=data[0],
            rows=data[1],
            table_title=f"Movies by {username}",
        )


movies_average_rating_blueprint = Blueprint("movies_average_rating_blueprint", __name__)
movies_blueprint.register_blueprint(
    movies_average_rating_blueprint, url_prefix="/average_rating"
)


@movies_average_rating_blueprint.route("/")
def view_average_rating_of_a_movie():
    return render_template(
        "MoviesAverageRating.html", fields=[], rows=[], table_title=""
    )


@movies_average_rating_blueprint.route("/results", methods=["POST"])
def results_average_rating():
    if request.method == "POST":
        data = request.form
        movie_id = data["movie_id"]
        query = f"select m.movie_id, m.movie_name, m.average_rating as overall_rating from movie m where m.movie_id = {movie_id}"
        data = postgres_aws.get_rows_and_fields_from_sql(query)
        if not data:
            return render_template(
                "MoviesAverageRating.html",
                fields=[],
                rows=[],
                table_title=f"No movie with id {movie_id}",
            )
        return render_template(
            "MoviesAverageRating.html",
            fields=data[0],
            rows=data[1],
            table_title=f"Average rating of the movie id {movie_id}",
        )
