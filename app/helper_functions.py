from clients.postgres.postgresql_db import postgres_aws
from datetime import datetime

def create_user(username: str, password: str, name: str, surname: str):
    return postgres_aws.write(
        f"""insert into "User" (username, password, name, surname) values ('{username}','{password}','{name}','{surname}')"""
    )


def create_director(username: str, nation_id: int):
    return postgres_aws.write(
        f"""insert into directors (username, nation_id) values ('{username}', {nation_id})"""
    )


def create_audience(username: str):
    return postgres_aws.write(
        f"""insert into audience (username) values ('{username}')"""
    )


def define_director_platform(username: str, platform_id: int):
    return postgres_aws.write(
        f"""insert into directorworkswith (username, platform_id) values ('{username}', {platform_id})"""
    )

def validate_date(date_string):
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d") # the format may vary based on your input
        return True
    except ValueError:
        return False