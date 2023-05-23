# Requirement: 5. Database managers shall be able to view all directors.
# The list must include the following attributes: username,
# name, surname, nation, platform id.

from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint
from .views import current_user, app
from functools import wraps

director_blueprint = Blueprint("director_blueprint", __name__)


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


@director_blueprint.route("/directors")
@login_required("Database_Manager")
def view_directors():
    query = """
    select d.username, u.name, u.surname, n.nation, dww.platform_id, rp.platform_name from directors d 
    join "User" u on d.username = u.username
    join nation n on d.nation_id = n.nation_id
    join directorworkswith dww on dww.username = d.username
    join ratingplatform rp on dww.platform_id = rp.platform_id
    """
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template(
        "TableView.html", fields=data[0], rows=data[1], table_title="Directors"
    )
