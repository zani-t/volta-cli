# SQL server functions and global variables

from mysql.connector import (
    connect,
    Error,
    CMySQLConnection,
    MySQLConnection,
)

from volta_cli import MYSQL_DATABASE_EXISTS, Login, config, SUCCESS, MYSQL_CONN_ERROR

def ping(login: Login) -> int:
    """ Test connection to MySQL and set object connection """
    try:
        with connect(
            host = login.hostname,
            user = login.username,
            password = login.password,
        ) as conn:
            pass
    except Error as e:
        print(e)
        return MYSQL_CONN_ERROR
    
    return SUCCESS

def init(login: Login) -> int:
    """ Create database volta if nonexistent """
    # Check if database exists (name volta)
    check_for_db_status = _check_for_db(login)
    if check_for_db_status:
        return MYSQL_DATABASE_EXISTS
    
    # Create database volta
    try:
        with connect(
            host = login.hostname,
            user = login.username,
            password = login.password,
        ) as conn:
            create_db_query = "CREATE DATABASE volta"
            with conn.cursor() as cursor:
                cursor.execute(create_db_query)
    except Error as e:
        print(e)
        return MYSQL_CONN_ERROR

    return SUCCESS

def _check_for_db(login: Login) -> int:
    """ Check for existence of database volta """
    # Return all databases by user name volta
    try:
        with connect(
            host = login.hostname,
            user = login.username,
            password = login.password,
        ) as conn:
            check_for_db_query = "SHOW DATABASES LIKE 'volta'"
            with conn.cursor() as cursor:
                cursor.execute(check_for_db_query)
                return len(cursor.fetchall())
    except Error as e:
        pass
    
    return MYSQL_CONN_ERROR