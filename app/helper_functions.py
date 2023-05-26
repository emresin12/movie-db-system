from clients.postgres.postgresql_db import postgres_aws


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


def get_predecessors(movie_id):
    # Query to get the predecessors
    query = f"""SELECT predecessor_movie_id FROM moviepredecessors WHERE followup_movie_id = {movie_id}"""
    print(query)
    # Execute the query
    result = postgres_aws.get(query)
    print(result)

    if result==[]:
        return []

    all_predecessors = [result[0]['predecessor_movie_id']]
    all_predecessors.extend(get_predecessors(result[0]['predecessor_movie_id']))

    return all_predecessors