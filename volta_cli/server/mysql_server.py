# SQL server functions and global variables

from mysql.connector import (
    connect,
    Error,
    CMySQLConnection,
    MySQLConnection,
)

from volta_cli import Login, SUCCESS, MYSQL_CONN_ERROR

connection: MySQLConnection | CMySQLConnection = None

def ping(login: Login) -> int:
    try:
        with connect(
            host = login.hostname,
            user = login.username,
            password = login.password,
        ) as conn:
            global connection
            connection = conn
    except Error as e:
        print(e)
        return MYSQL_CONN_ERROR
    
    return SUCCESS