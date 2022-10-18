# SQL server functions and global variables

from curses import ERR
from telnetlib import STATUS
from mysql.connector import connect, Error

from volta_cli import (
    Login,
    ERR_MYSQL_CONN, ERR_MYSQL_DB, ERR_MYSQL_QUERY, STATUS_MYSQL_DB_EX, STATUS_MYSQL_DB_NO_EX, SUCCESS,
    __app_name__,
)

def ping(login: Login) -> int:
    """ Test connection to MySQL """
    # Assert valid MySQL connection and make sure database is set to 'volta'
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
        ) as conn:
            if "database" in login.args:
                try:
                    conn.database = "volta"
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
    
    try:
        # Define database structure
        """ Model structure """
        create_db_query = "CREATE DATABASE volta"
        create_projects_query = """
        CREATE TABLE projects(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            dsc VARCHAR(255)
        )
        """
        create_modelsets_query = """
        CREATE TABLE modelsets(
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            name VARCHAR(100),
            dsc VARCHAR(255),
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
        """
        create_datasets_query = """
        CREATE TABLE datasets(
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            modelset_id INT,
            name VARCHAR(100),
            dsc VARCHAR(255),
            location TINYINT(1),
            address VARCHAR(255),
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(modelset_id) REFERENCES modelsets(id)
        )
        """
        create_models_query = """
        CREATE TABLE models(
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            modelset_id INT,
            dataset_id INT,
            name VARCHAR(100),
            dsc VARCHAR(255),
            arch VARCHAR(100),
            hyperparams VARCHAR(255),
            eval_metrics VARCHAR(255),
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(modelset_id) REFERENCES modelsets(id),
            FOREIGN KEY(dataset_id) REFERENCES datasets(id)
        )
        """
        create_endpoints_query = """
        CREATE TABLE endpoints(
            id INT AUTO_INCREMENT PRIMARY KEY,
            model_id INT,
            alias VARCHAR(100),
            location TINYINT(1),
            address VARCHAR(100),
            datatype VARCHAR(50),
            v_framework VARCHAR(50),
            total_runs INT,
            avg_runtime FLOAT,
            FOREIGN KEY(model_id) REFERENCES models(id)
        )
        """

        """ Initial entries """
        create_init_proj_query = """
        INSERT INTO projects (name, dsc)
        VALUES ("Unsorted", "Unsorted modelsets")
        """
        create_init_modelset_query = """
        INSERT INTO modelsets (project_id, name, dsc)
        VALUES (1, "Unsorted", "Unsorted models")
        """

        # Connect and run all queries
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_db_query)
                conn.commit()
                conn.database = "volta"
                for query in (
                    create_projects_query,
                    create_modelsets_query,
                    create_datasets_query,
                    create_models_query,
                    create_endpoints_query,
                    create_init_proj_query,
                    create_init_modelset_query,
                ):
                    cursor.execute(query)
                    print(query)
                    conn.commit()
    except Error as e:
        print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def destroy(login: Login) -> int:
    """ Destroy database 'volta' """
    # Check if database exists (name volta)
    check_for_db_status = _check_for_db(login)
    if not check_for_db_status:
        return STATUS_MYSQL_DB_NO_EX
    
    # Drop database volta
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
        ) as conn:
            create_db_query = "DROP DATABASE volta"
            with conn.cursor() as cursor:
                cursor.execute(create_db_query)
                conn.commit()
    except Error as e:
        print(e)
        return ERR_MYSQL_QUERY

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