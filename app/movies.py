# Requirement: 16. Audiences shall be able to list all the movies.
# The list must include the fol- lowing attributes: movie id, movie name,
# director’s surname, platform, theatre id, time slot, predecessors list.
# predecessors list must be a string in the form “movie1 id, movie2 id, ...”

from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint

movie_blueprint = Blueprint("director_blueprint", __name__)


@movie_blueprint.route("/movies")
def view_directors():
    query = """
    """
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template(
        "TableView.html", fields=data[0], rows=data[1], table_title="Directors"
    )
