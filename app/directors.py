# Requirement: 5. Database managers shall be able to view all directors.
# The list must include the following attributes: username,
# name, surname, nation, platform id.

from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint

director_blueprint = Blueprint(
    "director_blueprint", __name__
)


@director_blueprint.route('/directors')
def view_directors():
    query = """
    select d.username, u.name, u.surname, n.nation, dww.platform_id, rp.platform_name from directors d 
    join "User" u on d.username = u.username
    join nation n on d.nation_id = n.nation_id
    join directorworkswith dww on dww.username = d.username
    join ratingplatform rp on dww.platform_id = rp.platform_id
    """
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template('TableView.html', fields=data[0], rows=data[1], table_title='Directors')
