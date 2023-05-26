from clients.postgres.postgresql_db import postgres_aws


def get_table_fields(table_name):
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{}'
        order by ordinal_position asc
    """.format(
        table_name
    )
    response = postgres_aws.get(query)
    print(response)
    return [column["column_name"] for column in response]


def get_table_data(table_name):
    query = """
        SELECT *
        FROM {}
    """.format(
        table_name
    )
    rows = postgres_aws.get_as_list(query)
    print(rows)
    return rows


def get_table_info(table_name):
    fields = get_table_fields(table_name)
    rows = get_table_data(table_name)
    return fields, rows
