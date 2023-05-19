import os
from clients.postgres.base import PostgresBase


class PostgresAws(PostgresBase):
    def __init__(self):
        PostgresBase.__init__(
            self,
            host=os.environ.get("POSTGRES_HOST"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            database=os.environ.get("POSTGRES_DATABASE"),
        )


postgres_aws = PostgresAws()
