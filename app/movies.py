from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint, request

movies_blueprint = Blueprint("movies_blueprint", __name__)


@movies_blueprint.route("/")
def view_movies_home_page():
    return render_template(
        "MoviesHome.html"
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
                "MoviesViewRatingsByAudience.html", fields=[], rows=[], table_title=f"No ratings for {username}"
            )
        return render_template(
            "MoviesViewRatingsByAudience.html", fields=data[0], rows=data[1], table_title=f"Movie Ratings for {username}"
        )


movies_by_director_blueprint = Blueprint("movies_by_director_blueprint", __name__)
movies_blueprint.register_blueprint(movies_by_director_blueprint, url_prefix="/by_director")


@movies_by_director_blueprint.route("/")
def view_movies_by_director():
    return render_template(
        "MoviesByDirector.html", fields=[], rows=[], table_title=""
    )


@movies_by_director_blueprint.route("/results", methods=["POST"])
def results_by_director():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        query = f"select m.movie_id, m.movie_name, (select t.theatre_id from moviesession ms join theatre t on ms.theatre_id = t.theatre_id where ms.movie_id = m.movie_id limit 1) as theatre_id, (select t.theatre_district from moviesession ms join theatre t on ms.theatre_id = t.theatre_id where ms.movie_id = m.movie_id limit 1) as district, (select ms.time_slot from moviesession ms join theatre t on ms.theatre_id = t.theatre_id where ms.movie_id = m.movie_id limit 1) as time_slot from movie m where m.director_username = '{username}'"
        data = postgres_aws.get_rows_and_fields_from_sql(query)
        if not data:
            return render_template(
                "MoviesByDirector.html", fields=[], rows=[], table_title=f"No movies for {username}"
            )
        return render_template(
            "MoviesByDirector.html", fields=data[0], rows=data[1],
            table_title=f"Movies by {username}"
        )


movies_average_rating_blueprint = Blueprint("movies_average_rating_blueprint", __name__)
movies_blueprint.register_blueprint(movies_average_rating_blueprint, url_prefix="/average_rating")


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
                "MoviesAverageRating.html", fields=[], rows=[], table_title=f"No movie with id {movie_id}"
            )
        return render_template(
            "MoviesAverageRating.html", fields=data[0], rows=data[1],
            table_title=f"Average rating of the movie id {movie_id}"
        )