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
        if self.connection:
            return self.connection
        else:
            connection = psycopg2.connect(
                database=self.database, user=self.user,
                password=self.password, host=self.host
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
