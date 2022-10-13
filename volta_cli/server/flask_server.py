from flask import Flask
from flask_restful import Resource, Api

from volta_cli import SUCCESS, MYSQL_CONN_ERROR
from volta_cli.server import mysql_server

app = Flask(__name__)
api = Api(app)

def start():
    # mysql_server.ping()

# def update