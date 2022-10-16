from flask import Flask
from flask_restful import Resource, Api

from volta_cli import SUCCESS
from volta_cli.server import mysql_server

app = Flask(__name__)
api = Api(app)

def start():
    """ start -> Run Flask server with updated endpoints """
    # update()
    app.run()

    return SUCCESS

# def update