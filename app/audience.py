# 2. Database managers shall be able to add new Users (Audiences or Directors)
# to the system.
from clients.postgres.postgresql_db import postgres_aws
from flask import render_template, Blueprint, request, redirect, flash, url_for
from app.helper_functions import create_audience, create_user, define_director_platform, get_predecessors
from pydantic import BaseModel
from functools import wraps
from .views import current_user

audience_blueprint = Blueprint("audience_blueprint", __name__)



def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return render_template(
                    "login.html"
                )  # this should be the right method to call unauthorized view
            urole = current_user._get_current_object().get_urole()
            print(urole)
            if (urole != role) and (role != "ANY"):
                return render_template("index.html", error="not authorized")
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


@audience_blueprint.route("/audience")
def directors_home_page():
    return render_template("AudienceHome.html")


@audience_blueprint.route("/list")
def view_audience():
    query = """
    select u.username, u.name, u.surname from audience a 
    join "User" u on a.username = u.username
    """
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template(
        "TableView.html", fields=data[0], rows=data[1], table_title="Audience"
    )


@audience_blueprint.route("/create")
def create_audience_page():
    return render_template("AudienceCreate.html")


class AudienceCreateRequestObject(BaseModel):
    username: str
    password: str
    name: str
    surname: str

    def insert_to_database(self):
        create_user(
            username=self.username,
            password=self.password,
            name=self.name,
            surname=self.surname,
        )
        create_audience(username=self.username)
        return True


@audience_blueprint.route("/create_submit", methods=["POST"])
def submit():
    if request.method == "POST":
        # Access the form data
        data = request.form
        try:
            obj = AudienceCreateRequestObject(**data)
            obj.insert_to_database()
        except Exception as e:
            flash(str(e.args), "error")
            return redirect(url_for("audience_blueprint.create_audience_page"))
    flash("Audience is created successfully!", "success")
    return redirect(url_for("audience_blueprint.create_audience_page"))

@audience_blueprint.route("/audience/delete", methods=["POST","GET"])
def delete_audience():
    if request.method == "POST":
        data = request.form
        username = data["username"]

        res = postgres_aws.get(f"""select * from Audience where username = '{username}'""") # check if it is an audience 
        if len(res) == 0:
            flash("User is not an audience!", "error")
            return redirect(url_for("audience_blueprint.delete_audience"))
        query = f"""
        delete from "User" where username = '{username}'
        """
        postgres_aws.write(query)
        return redirect(url_for("audience_blueprint.view_audience"))
    
    return render_template("DeleteAudienceByManager.html")

#16. Audiences shall be able to list all the movies. The list must include the fol- lowing attributes:
#  movie id, movie name, director’s surname, platform, theatre id, time slot, predecessors list. 
# predecessors list must be a string in the form “movie1 id, movie2 id, ...”
@audience_blueprint.route("/audience/list_movies", methods=["GET"])
def list_movies():
        query = """select m.movie_id,m.movie_name, u.surname, d.platform_id,s.theatre_id,s.time_slot  from movie m
        join "User" u on m.director_username= u.username
        join directorworkswith d on u.username = d.username
        join moviesession s on m.movie_id = s.movie_id;""" 
        data = postgres_aws.get_rows_and_fields_from_sql(query)
        #I want to get all movie_id 's in data and then get predecessors for each movie_id

        movieList = []
        print(data)

        for row in data[1]:
            movieList.append(row[0])
        predlists = {}
        for movie in movieList:
            predList = get_predecessors(movie)
            predlists[movie] = predList
        
        data[0].append("Predecessors")
        for row in data[1]:
            #row.append(",".join(predlists[row[0]]))
            row.append(",".join([str(item) for item in predlists[row[0]]]))

        return render_template("TableView.html", fields=data[0], rows=data[1], table_title="Movies")


@audience_blueprint.route("/audience/buy_ticket", methods=["GET","POST"])
def buy_ticket():
    if request.method == "POST":
        data = request.form
        session_id = data["session_id"]
        username = current_user.get_id()
        print(username, "BU USER NAME ------------------------------------------------")

        query = f"""select * from moviesessiontickets where username = '{username}' and session_id = {session_id}"""
        res = postgres_aws.get(query)
        if len(res) != 0:
            return render_template("AudienceBuyTicket.html", error="You have already bought a ticket for this session!")

        #check for is there is enough space in the theatre
        query = f"""select t.theatre_capacity from moviesession m join theatre t on t.theatre_id = m.theatre_id where session_id = {session_id}"""
        capacity = postgres_aws.get(query)[0]["theatre_capacity"]
        query = f"""select count(*) from moviesessiontickets where session_id = {session_id}"""
        ticket_count = postgres_aws.get(query)[0]["count"]

        if(ticket_count >= capacity):
            return render_template("AudienceBuyTicket.html", error="There is no space in the theatre!")



        #check if user has watched all the predecessors of the movie before.
        query = f"""select m.movie_id, m.date from moviesession m where session_id = {session_id}"""
        ret = postgres_aws.get(query)

        movie_id = ret[0]["movie_id"]
        date = ret[0]["date"]  

        predList = get_predecessors(movie_id)

        #gets all the movies that user has watched before the date of the movie that he is trying to buy ticket for
        query = f"""select m.movie_id from moviesession m join moviesessiontickets t on m.session_id = t.session_id where t.username = '{username}' and m.date < '{date}' """
        res = postgres_aws.get(query) # we get all the movies that user has watched
        movies_watched = [d['movie_id'] for d in res]

        flag = True

        for pred in predList:#if predlist is empty its already true
            if pred in movies_watched:
                pass
            else:
                flag = False
                break
        
        if flag == False:
            return render_template("AudienceBuyTicket.html", error="You have to watch all the predecessors of the movie before!")
        else:
            query = f"""insert into moviesessiontickets (username,session_id) values ('{username}', {session_id})"""
            postgres_aws.write(query)
            return "Ticket is bought successfully"
        

    else:
        return render_template("AudienceBuyTicket.html")

@audience_blueprint.route("/audience/view_tickets", methods=["GET"])
def view_tickets():
    username = current_user.get_id()
    query = f"""SELECT
m.movie_id,
m.movie_name,
s.session_id,
r.rating,
m.average_rating as overall_rating
FROM
    MovieSessionTickets t
JOIN
    MovieSession s ON t.session_id = s.session_id
JOIN
    Movie m on m.movie_id = s.movie_id
JOIN
    Ratings r ON r.username = t.username
WHERE
    t.username = '{username}';"""
    data = postgres_aws.get_rows_and_fields_from_sql(query)
    return render_template("TableView.html", fields=data[0], rows=data[1], table_title="Tickets")
