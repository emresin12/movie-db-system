from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint


def get_table_fields(table_name):
    response = postgres_aws.get("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{}'
    """.format(table_name))
    return [column['column_name'] for column in response]


def get_table_data(table_name):
    rows = postgres_aws.get_as_list("""
        SELECT *
        FROM {}
    """.format(table_name))
    return rows


def get_table_info(table_name):
    fields = get_table_fields(table_name)
    rows = get_table_data(table_name)
    return fields, rows


crud_table_blueprint = Blueprint(
  "crud_table_blueprint", __name__
)


@crud_table_blueprint.route('/testing')
def test():
    table_name = 'ratingplatform'
    data = get_table_info(table_name)
    return render_template('test.html', fields=data[0], rows=data[1], table_name=table_name)
