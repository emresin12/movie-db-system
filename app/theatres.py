from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint, request
from functools import wraps
from .views import current_user

theatres_blueprint = Blueprint("theatres_blueprint", __name__)


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


@theatres_blueprint.route("/")
def theatres_home_page():
    return render_template("TheatresHome.html")



@theatres_blueprint.route("/available_list", methods=["GET", "POST"])
@login_required(role="Director")
def avilable_theatre_list_page():
    if request.method == "GET":
        return render_template("AvailableTheatres.html")
    elif request.method == "POST":
        input = request.form
        query = f"select t.theatre_id, t.theatre_name, t.theatre_district from theatre t where t.theatre_id not in (select ms.theatre_id from moviesession ms join theatre t2 on ms.theatre_id = t2.theatre_id join movie m on ms.movie_id = m.movie_id where ms.date = '{input['input_date']}' and {input['time_slot']} between ms.time_slot and ms.time_slot + m.duration - 1)"
        data = postgres_aws.get_rows_and_fields_from_sql(query)
        if not data:
            return render_template(
                "AvailableTheatres.html",
                fields=[],
                rows=[],
                table_title=f"No theatre available on {data['input_date']} and time slot: {data['time_slot']}",
            )
        return render_template(
            "AvailableTheatres.html",
            fields=data[0],
            rows=data[1],
            table_title=f"Available Theatres on {input['input_date']} and time slot: {input['time_slot']}",
        )
        return render_template("AvailableTheatres.html")
