# SQL server functions and global variables

from curses import ERR
from telnetlib import STATUS
from mysql.connector import connect, Error

from volta_cli import (
    Login, LoginResponse,
    ERR_MYSQL_CONN, ERR_MYSQL_DB, STATUS_MYSQL_DB_EX, SUCCESS,
    __app_name__,
)

def ping(login: Login) -> int:
    """ Test connection to MySQL and set object connection """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
        ) as conn:
            if "database" in login.args:
                try:
                    conn.database = "test"
                except Error as e:
                    print(e)
                    return ERR_MYSQL_DB
    except Error as e:
        print(e)
        return ERR_MYSQL_CONN
    
    return SUCCESS

""" DATABASE LEVEL FUNCTIONS """

def init(login: Login) -> int:
    """ Create database volta if nonexistent """
    # Check if database exists (name volta)
    check_for_db_status = _check_for_db(login)
    if check_for_db_status:
        return STATUS_MYSQL_DB_EX
    
    # Create database volta
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
        ) as conn:
            create_db_query = "CREATE DATABASE volta"
            with conn.cursor() as cursor:
                cursor.execute(create_db_query)
    except Error as e:
        print(e)
        return ERR_MYSQL_CONN

    return SUCCESS

def _check_for_db(login: Login) -> int:
    """ Check for existence of database volta """
    # Return all databases by user name volta
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
        ) as conn:
            check_for_db_query = "SHOW DATABASES LIKE 'volta'"
            with conn.cursor() as cursor:
                cursor.execute(check_for_db_query)
                if len(cursor.fetchall()):
                    return STATUS_MYSQL_DB_EX
                return SUCCESS

    except Error as e:
        pass
    
    return ERR_MYSQL_CONN

""" PROJECT LEVEL COMMANDS """



""" GROUP LEVEL COMMANDS """

""" MODEL LEVEL COMMANDS """ 