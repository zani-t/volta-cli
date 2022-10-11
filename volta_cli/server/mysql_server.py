# SQL server functions and global variables

from mysql.connector import (
    connect,
    Error,
    CMySQLConnection,
    MySQLConnection,
)

from volta_cli import SUCCESS, MYSQL_LOGIN_ERROR

g_hostname: str = 'localhost'
g_username: str = 'root'
g_password: str = None

connection: MySQLConnection | CMySQLConnection = None

def set_credentials(
    hostname: str,
    username: str,
    password: str,
) -> int:
    try:
        with connect(
            host = hostname,
            user = username,
            password = password,
        ) as conn:

            global g_hostname, g_username, g_password, connection
            g_hostname = hostname
            g_username = username
            g_password = password
            #connection = conn

            return SUCCESS

    except Error:
        return MYSQL_LOGIN_ERROR