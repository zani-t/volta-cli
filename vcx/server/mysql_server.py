# SQL server functions and global variables

from mysql.connector import connect, Error

from vcx import (
    Login, IDResponse, RawResponse,
    ERR_MYSQL_CONN, ERR_MYSQL_QUERY, STATUS_MYSQL_DB_EX, STATUS_MYSQL_DB_NO_EX,
    STATUS_MYSQL_PROJ_EX, STATUS_MYSQL_PROJ_NO_EX, SUCCESS,
    __app_name__,
)

def ping(
    login: Login,
    ping_project: bool = False,
    proj_name: str = "Unsorted",
    modelset_name: str = "Unsorted",
) -> int:
    """ Test connection to MySQL """
    check_for_db_status = _check_for_db(login)
    # Connection error
    if check_for_db_status == ERR_MYSQL_CONN:
        return ERR_MYSQL_CONN

    # Valid connection, database 'volta' does not exist
    if not check_for_db_status:
        return STATUS_MYSQL_DB_NO_EX
    
    if ping_project:
        check_for_proj_status = _check_for_project(login, proj_name, modelset_name)
        if check_for_proj_status:
            return check_for_proj_status
    
    # Valid connection
    return SUCCESS

def raw(login: Login, query: str) -> RawResponse:
    """ Execute raw MySQL commands (intended for sorting) """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                output = map(str, cursor.fetchall())
                return ("\n".join(output), SUCCESS)
    except Error as e:
        # print(e)
        pass
    
    return (None, ERR_MYSQL_QUERY)

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
        VALUES ("Unsorted", "Unsorted groups/modelsets")
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

def get_id(login: Login, level: str, name: str) -> IDResponse:
    """ Get ID of entry """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            get_id_query = f"SELECT id FROM {level} WHERE name = '{name}'"
            with conn.cursor() as cursor:
                # Try block obsolete in with block???
                cursor.execute(get_id_query)
                entry = cursor.fetchone()
                if not entry:
                    return (None, ERR_MYSQL_QUERY)
                return (list(entry)[0], SUCCESS)

    except Error as e:
        print(e)
        return (None, ERR_MYSQL_QUERY)

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

def _check_for_project(login: Login, proj_name: str, modelset_name: str) -> int:
    """ Check for existence of project & modelset """
    # Return all projects of name name
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta"
        ) as conn:
            check_for_proj_query = f"SELECT * FROM projects WHERE name = '{proj_name}'"
            with conn.cursor() as cursor:
                cursor.execute(check_for_proj_query)
                if not len(cursor.fetchall()):
                    return STATUS_MYSQL_PROJ_NO_EX
            check_for_ms_query = f"SELECT * FROM modelsets WHERE name = '{modelset_name}'"
            with conn.cursor() as cursor:
                cursor.execute(check_for_ms_query)
                if not len(cursor.fetchall()):
                    return STATUS_MYSQL_PROJ_NO_EX

    except Error as e:
        return ERR_MYSQL_CONN
    
    return SUCCESS

""" PROJECT LEVEL COMMANDS """

def createproj(login: Login, name: str, desc: str) -> int:
    """ Create project """
    # Create project with given name and description
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            duplicate = _check_duplicate(login, "projects", name)
            if duplicate:
                return STATUS_MYSQL_PROJ_EX
            
            create_query = f"""
            INSERT INTO projects (name, dsc)
            VALUES ("{name}", "{desc}")
            """
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                print("executed")
                conn.commit()
                print("committed")
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def deleteproj(login: str, name: str) -> int:
    """ Delete project """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            proj_id, get_proj_id_error = get_id(login, "projects", name)
            # print(proj_id, get_proj_id_error)
            if get_proj_id_error:
                return get_proj_id_error

            # Delete all models with projet id project name id
            delete_models_query = f"DELETE FROM models WHERE project_id = {proj_id}"
            # Delete all datasets
            delete_dataset_query = f"DELETE FROM datasets WHERE project_id = {proj_id}"
            # Delete all modelsets
            delete_modelset_query = f"DELETE FROM modelsets WHERE project_id = {proj_id}"
            # Delete project
            delete_project_query = f"DELETE FROM projects where id = {proj_id}"
            with conn.cursor() as cursor:
                for query in (
                    delete_models_query,
                    delete_dataset_query,
                    delete_modelset_query,
                    delete_project_query,
                ):
                    print(query)
                    cursor.execute(query)
                    conn.commit()
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def _check_duplicate(login: Login, level: str, name: str) -> int:
    """ unfinished Check for duplicate names in database """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            check_duplicate_query = f"""
            SELECT * FROM {level} WHERE name = '{name}'
            """
            with conn.cursor() as cursor:
                cursor.execute(check_duplicate_query)
                return len(cursor.fetchall())
    except Error as e:
        pass

    return ERR_MYSQL_QUERY

""" MODELSET LEVEL COMMANDS """

def createmset(login: Login, project: str, name: str, desc: str) -> int:
    """ Create modelset """
    # Create modelset with given name and description
    try:
        print("creating group")
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            duplicate = _check_duplicate(login, "modelsets", name)
            if duplicate:
                return STATUS_MYSQL_PROJ_EX
                
            proj_id, get_proj_id_error = get_id(login, "projects", project)
            if get_proj_id_error:
                return get_proj_id_error

            create_query = f"""
            INSERT INTO modelsets (project_id, name, dsc)
            VALUES ({proj_id}, "{name}", "{desc}")
            """
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                conn.commit()
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def deletemset(login: str, name: str) -> int:
    """ Delete modelset """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            mset_id, get_mset_id_error = get_id(login, "modelsets", name)
            if get_mset_id_error:
                return get_mset_id_error

            # Delete all models with projet id project name id
            delete_models_query = f"DELETE FROM models WHERE project_id = {mset_id}"
            # Delete all modelsets
            delete_modelset_query = f"DELETE FROM modelsets WHERE project_id = {mset_id}"
            with conn.cursor() as cursor:
                cursor.execute(delete_models_query)
                cursor.execute(delete_modelset_query)
                conn.commit()
            
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

""" MODEL LEVEL COMMANDS """ 

