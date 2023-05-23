import psycopg2
import psycopg2.extras


class PostgresBase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def get_connection(self):
        if self.connection and self.connection.closed == 0:
            return self.connection
        else:
            connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
            )
            connection.autocommit = True
            self.connection = connection
            return connection

    def write(self, query):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        cursor.close()
        return {"status": "success"}

    def get(self, query):
        connection = self.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query)
        ans = cursor.fetchall()
        dict_result = []
        for row in ans:
            dict_result.append(dict(row))
        cursor.close()
        return dict_result

    def get_as_list(self, query):
        connection = self.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query)
        ans = cursor.fetchall()
        cursor.close()
        return ans

    def get_rows_and_fields_from_sql(self, query):
        connection = self.get_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query)
        ans = cursor.fetchall()
        dict_result = []
        for row in ans:
            dict_result.append(dict(row))
        cursor.close()
        if not dict_result:
            return []
        else:
            fields = list(dict_result[0].keys())
            array_of_values = []
            for dictionary in dict_result:
                values = list(dictionary.values())
                array_of_values.append(values)
            rows = array_of_values
            return fields, rows
