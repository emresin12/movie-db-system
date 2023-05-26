POSTGRES_HOST=ec2-18-134-207-44.eu-west-2.compute.amazonaws.com
POSTGRES_USER=ubuntu
POSTGRES_PASSWORD=cmpe321project3
POSTGRES_DATABASE=project3
SECRET_KEY=emrehalis123

Before running the app we should set enviroment variables. To do so we modify .env.example to .env and change its content with the credentials given above.

1-In terminal go to movie-db-system directory.
2- create virtual enviroment by “python3 -m venv venv”
3- activate virtual environment by “. Venv/bin/activate”
4- to install requirements use “pip3 install -r requirements.txt”
5- run application by “flask run”