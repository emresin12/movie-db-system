from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint, request


def get_table_fields(table_name):
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{}'
        order by ordinal_position asc
    """.format(table_name)
    response = postgres_aws.get(query)
    print(response)
    return [column['column_name'] for column in response]


def get_table_data(table_name):
    query = """
        SELECT *
        FROM {}
    """.format(table_name)
    rows = postgres_aws.get_as_list(query)
    print(rows)
    return rows


def get_table_info(table_name):
    fields = get_table_fields(table_name)
    rows = get_table_data(table_name)
    return fields, rows


crud_table_blueprint = Blueprint(
    "crud_table_blueprint", __name__
)


@crud_table_blueprint.route('/examplecrud')
def example1():
    table_name = 'theatretest'
    primary_key = "theatre_id"
    data = get_table_info(table_name)
    return render_template('CrudTable.html', fields=data[0], rows=data[1], table_name=table_name,
                           primary_key=primary_key)


@crud_table_blueprint.route('/submit', methods=['POST'])
def submit():
    # Handle the form submission here
    table_name = 'theatretest'
    primary_key = "theatre_id"
    if request.method=='POST':
        # Access the form data
        data = request.form
        for key, value in data.items():
            print(key, value)
        columns = data.keys()
        values = [f"'{value}'" for value in data.values()]

        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)})"
        query += f" ON CONFLICT ({primary_key}) DO UPDATE SET "
        query += ", ".join([f"{key} = '{value}'" for key, value in data.items()])

        try:
            postgres_aws.write(query)
            return "Database is Updated Successfully!"
        except Exception as e:
            return str(e)


@crud_table_blueprint.route('/delete', methods=['POST'])
def delete():
    # Handle the form submission here
    table_name = "theatretest"
    primary_key = "theatre_id"
    if request.method == 'POST':
        # Access the form data
        data = request.form
        primary_key_value = data['primary_key_value']
        query = f"DELETE FROM {table_name} WHERE {primary_key} = '{primary_key_value}'"
        postgres_aws.write(query)
        return "Object is deleted successfully!"


@crud_table_blueprint.route('/exampleview')
def example2():
    query = """select sub.username                          as username,
       sub.password                          as password,
       (case
            when (select count(*) > 0 from audience where sub.username = audience.username) then 'Audience'
            when (select count(*) > 0 from directors where sub.username = directors.username) then 'Director'
            when (select count(*) > 0 from databasemanagers where sub.username = databasemanagers.username)
                then 'Database Manager' end) as user_role
from (select u.username, u.password
      from "User" u
      union all
      select dm.username, dm.password
      from databasemanagers dm) sub"""
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template('TableView.html', fields=data[0], rows=data[1], table_title='All Users')
