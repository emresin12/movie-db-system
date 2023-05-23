# Requirement: 16. Audiences shall be able to list all the movies.
# The list must include the fol- lowing attributes: movie id, movie name,
# director’s surname, platform, theatre id, time slot, predecessors list.
# predecessors list must be a string in the form “movie1 id, movie2 id, ...”

from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint
from .views import current_user, app
from functools import wraps

movie_blueprint = Blueprint("director_blueprint", __name__)


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            with app.app_context():  # Create a temporary application context
                if not current_user.is_authenticated:
                    return app.login_manager.unauthorized()
                urole = current_user._get_current_object().get_urole()
                print(urole)
                if (urole != role) and (role != "ANY"):
                    return render_template("index.html", error="not authorized")
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper
  
  
@movie_blueprint.route("/movies")
def view_directors():
    query = """
    """
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template(
        "TableView.html", fields=data[0], rows=data[1], table_title="Directors"
    )
