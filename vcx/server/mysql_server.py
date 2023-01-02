# SQL server functions and global variables

from mysql.connector import connect, Error

from vcx import (
    Login, DatasetResponseSQL, IDResponse, ModelResponse, RawResponse, ScriptResponse,
    ERR_MYSQL_CONN, ERR_MYSQL_QUERY, STATUS_MYSQL_DB_EX, STATUS_MYSQL_DB_NO_EX,
    STATUS_MYSQL_PROJ_EX, STATUS_MYSQL_PROJ_NO_EX, STATUS_MYSQL_ENTRY_NO_EX, STATUS_MYSQL_ENTRY_EX, SUCCESS,
    __app_name__,
)

def ping(
    login: Login,
    ping_project: bool = False,
    proj_name: str = "Unsorted",
    modelset_name: str = "Unsorted",
    script_name: str = "",
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
        check_for_proj_status = _check_for_project(login, proj_name, modelset_name, script_name)
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
        create_scripts_query = """
        CREATE TABLE scripts(
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            modelset_id INT,
            dataset_id INT,
            name VARCHAR(100),
            dsc VARCHAR(255),
            script VARCHAR(4096),
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(modelset_id) REFERENCES modelsets(id),
            FOREIGN KEY(dataset_id) REFERENCES datasets(id)
        )
        """
        create_models_query = """
        CREATE TABLE models(
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT,
            modelset_id INT,
            name VARCHAR(100),
            dsc VARCHAR(255),
            arch VARCHAR(100),
            FOREIGN KEY(project_id) REFERENCES projects(id),
            FOREIGN KEY(modelset_id) REFERENCES modelsets(id)
        )
        """
        create_endpoints_query = """
        CREATE TABLE endpoints(
            id INT AUTO_INCREMENT PRIMARY KEY,
            model_id INT,
            alias VARCHAR(100),
            dataset VARCHAR(100),
            location TINYINT(1),
            address VARCHAR(100),
            datatype VARCHAR(255),
            v_framework VARCHAR(50),
            deployed TINYINT(1),
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
                    create_scripts_query,
                    create_models_query,
                    create_endpoints_query,
                    create_init_proj_query,
                    create_init_modelset_query,
                ):
                    cursor.execute(query)
                    conn.commit()
    except Error as e:
        # print(e)
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
        # print(e)
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
            ext = ''
            if level != 'projects':
                proj_id, get_proj_id_error = get_id(login, "projects", login.args["project"])
                # print("proj_id", proj_id)
                if get_proj_id_error:
                    return (None, get_proj_id_error)
                ext += f' AND project_id = {proj_id}'
                if level != 'modelsets':
                    ms_id, get_ms_id_error = get_id(login, "modelsets", login.args["modelset"])
                    # print("ms_id", ms_id)
                    if get_ms_id_error:
                        return (None, get_ms_id_error)
                    ext += f' AND modelset_id = {ms_id}'
            get_id_query += ext
            # print(get_id_query)

            with conn.cursor() as cursor:
                cursor.execute(get_id_query)
                entry = cursor.fetchone()
                if not entry:
                    return (None, ERR_MYSQL_QUERY)
                return (list(entry)[0], SUCCESS)

    except Error as e:
        # print(e)
        pass
    
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

def _check_for_project(login: Login, proj_name: str, modelset_name: str, script_name: str) -> int:
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
                    return STATUS_MYSQL_ENTRY_NO_EX
            if script_name != "":
                check_for_script_query = f"SELECT * FROM scripts WHERE name = '{script_name}'"
                with conn.cursor() as cursor:
                    cursor.execute(check_for_script_query)
                    if not len(cursor.fetchall()):
                        return STATUS_MYSQL_ENTRY_NO_EX

    except Error as e:
        return ERR_MYSQL_CONN
    
    return SUCCESS

def _check_duplicate(login: Login, level: str, name: str, script_ds: str=None) -> int:
    """ Check for duplicate names in database """
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
            # modelset -> unique per project
            # dataset -> unique per modelset
            # script -> unique per dataset
            # model -> unique per modelset
            ext = ''
            if level != 'projects':
                proj_id, get_proj_id_error = get_id(login, "projects", login.args["project"])
                # print("get_proj_id_error", get_proj_id_error)
                if get_proj_id_error:
                    return get_proj_id_error
                ext += f' AND project_id = {proj_id}'
                # print([login.args["project"], str(proj_id), ext])
                if level != 'modelsets':
                    ms_id, get_ms_id_error = get_id(login, "modelsets", login.args["modelset"])
                    # print("get_ms_id_error", get_ms_id_error)
                    if get_ms_id_error:
                        return get_ms_id_error
                    ext += f' AND modelset_id = {ms_id}'
                if level == 'scripts':
                    ds_id, get_ds_id_error = get_id(login, "datasets", script_ds)
                    # print("get_ds_id_error", get_ds_id_error)
                    if get_ds_id_error:
                        return get_ds_id_error
                    ext += f' AND dataset_id = {ds_id}'
            check_duplicate_query += ext
            # print("check_duplicate_query", check_duplicate_query)

            with conn.cursor() as cursor:
                cursor.execute(check_duplicate_query)
                return len(cursor.fetchall())
    except Error as e:
        pass

    return ERR_MYSQL_QUERY

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
                conn.commit()
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
                    cursor.execute(query)
                    conn.commit()
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

""" MODELSET LEVEL COMMANDS """

def createmset(login: Login, proj_name: str, name: str, desc: str) -> int:
    """ Create modelset """
    # Create modelset with given name and description
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            # Set current project to given project name
            login.args["project"] = proj_name
            # Search for modelset (default 'Unsorted') in project
            duplicate = _check_duplicate(login, "modelsets", name)
            if duplicate:
                return STATUS_MYSQL_ENTRY_EX
                
            proj_id, get_proj_id_error = get_id(login, "projects", proj_name)
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

            # Delete all models with modelset id modelset name id
            delete_models_query = f"DELETE FROM models WHERE modelset_id = {mset_id}"
            # Delete all scripts with modelset id modelset name id
            delete_scripts_query = f"DELETE FROM scripts WHERE modelset_id = {mset_id}"
            # Delete all datasets with modelset id modelset name id
            delete_datasets_query = f"DELETE FROM datasets WHERE modelset_id = {mset_id}"
            # Delete all modelsets
            delete_modelset_query = f"DELETE FROM modelsets WHERE id = {mset_id}"
            with conn.cursor() as cursor:
                cursor.execute(delete_models_query)
                cursor.execute(delete_scripts_query)
                cursor.execute(delete_datasets_query)
                cursor.execute(delete_modelset_query)
                conn.commit()
            
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

""" DATASET LEVEL COMMANDS """ 

def createdataset(login: Login, name: str, desc: str, location: int, address: str) -> int:
    """ Create dataset """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            
            duplicate = _check_duplicate(login, "datasets", name)
            if duplicate:
                return STATUS_MYSQL_PROJ_EX
            
            proj_id, get_proj_id_error = get_id(login, "projects", login.args["project"])
            if get_proj_id_error:
                return get_proj_id_error
            
            ms_id, get_ms_id_error = get_id(login, "modelsets", login.args["modelset"])
            if get_ms_id_error:
                return get_ms_id_error
            
            create_query = f"""
            INSERT INTO datasets (project_id, modelset_id, name, dsc, location, address)
            VALUES ({proj_id}, {ms_id}, "{name}", "{desc}", {location}, "{address}")
            """
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                conn.commit()
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def deletedataset(login: str, name: str) -> int:
    """ Delete dataset """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            dset_id, get_dset_id_error = get_id(login, "datasets", name)
            if get_dset_id_error:
                return get_dset_id_error

            # Delete all datasets
            delete_dataset_query = f"DELETE FROM datasets WHERE id = {dset_id}"
            with conn.cursor() as cursor:
                cursor.execute(delete_dataset_query)
                conn.commit()
            
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def getdataset(login: str, name: str=None, id: int=None) -> DatasetResponseSQL:
    """ Retrieve str dataset address """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            create_query = f'SELECT location, address FROM datasets WHERE name = "{name}"'
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                response = cursor.fetchall()
                if not len(response):
                    return (None, None, STATUS_MYSQL_ENTRY_NO_EX)
                
                location, address = response[0]
                return (int(location), address, SUCCESS)
    except Error as e:
        # print(e)
        pass
        
    return ERR_MYSQL_QUERY

""" PREPROCESSING SCRIPT LEVEL COMMANDS """

def createscript(login: Login, name: str, desc: str, dataset: str) -> int:
    """ Create preprocessing script """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            
            duplicate = _check_duplicate(login, "scripts", name, script_ds=dataset)
            if duplicate:
                return duplicate
            
            proj_id, get_proj_id_error = get_id(login, "projects", login.args["project"])
            if get_proj_id_error:
                return get_proj_id_error
            
            ms_id, get_ms_id_error = get_id(login, "modelsets", login.args["modelset"])
            if get_ms_id_error:
                return get_ms_id_error
            
            ds_id, get_ds_id_error = get_id(login, "datasets", dataset)
            if get_ds_id_error:
                return get_ds_id_error
            
            create_query = f"""
            INSERT INTO scripts (project_id, modelset_id, dataset_id, name, dsc, script)
            VALUES ({proj_id}, {ms_id}, {ds_id}, "{name}", "{desc}", " ")
            """
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                conn.commit()
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def deletescript(login: str, name: str) -> int:
    """ Delete script """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            script_id, get_script_id_error = get_id(login, "scripts", name)
            if get_script_id_error:
                return get_script_id_error

            delete_script_query = f"DELETE FROM scripts WHERE id = {script_id}"
            with conn.cursor() as cursor:
                cursor.execute(delete_script_query)
                conn.commit()
            
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def getscript(login: str, name=None) -> ScriptResponse:
    """ Retrieve script test """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            # NARROW DOWN TO LOGIN CREDENTIALS
            get_query = ""
            if name:
                get_query = f'SELECT script FROM scripts WHERE name = "{name}"'
            else:
                get_query = f'SELECT script FROM scripts WHERE name = "{login.args["script"]}"'
            with conn.cursor() as cursor:
                cursor.execute(get_query)
                response = cursor.fetchall()
                if not len(response):
                    return (None, STATUS_MYSQL_ENTRY_NO_EX)
                script = response[0][0]
                return (script, SUCCESS)
    except Error as e:
        # print(e)
        pass
        
    return (None, ERR_MYSQL_QUERY)

def setscript(login: str, script: str) -> int:
    """ Retrieve script test """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            script_id, get_script_id_error = get_id(login, "scripts", login.args["script"])
            if get_script_id_error:
                return get_script_id_error

            set_script_query = f'UPDATE scripts SET script = "{script}" WHERE id = {script_id}'
            with conn.cursor() as cursor:
                cursor.execute(set_script_query)
                conn.commit()
            
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

""" MODEL LEVEL COMMANDS """ 

def createmodel(login: Login, name: str, desc: str, arch: int) -> int:
    """ Create untrained model """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            
            duplicate = _check_duplicate(login, "models", name)
            if duplicate:
                return STATUS_MYSQL_ENTRY_EX
            
            proj_id, get_proj_id_error = get_id(login, "projects", login.args["project"])
            if get_proj_id_error:
                return get_proj_id_error
            
            ms_id, get_ms_id_error = get_id(login, "modelsets", login.args["modelset"])
            if get_ms_id_error:
                return get_ms_id_error
            
            create_query = f"""
            INSERT INTO models (project_id, modelset_id, name, dsc, arch)
            VALUES ({proj_id}, {ms_id}, "{name}", "{desc}", "{arch}")
            """
            # print(create_query)
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                conn.commit()
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def deletemodel(login: str, name: str) -> int:
    """ Delete model """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            model_id, get_model_id_error = get_id(login, "models", name)
            if get_model_id_error:
                return get_model_id_error

            delete_script_query = f"DELETE FROM models WHERE id = {model_id}"
            with conn.cursor() as cursor:
                cursor.execute(delete_script_query)
                conn.commit()
            
    except Error as e:
        # print(e)
        return ERR_MYSQL_QUERY

    return SUCCESS

def getmodel(login: str, name: str) -> ModelResponse:
    """ Retrieve model """
    try:
        with connect(
            host = login.args["host"],
            user = login.args["user"],
            password = login.args["password"],
            database = "volta",
        ) as conn:
            # NARROW DOWN TO LOGIN CREDENTIALS
            create_query = f'SELECT * FROM models WHERE name = "{name}"'
            with conn.cursor() as cursor:
                cursor.execute(create_query)
                response = cursor.fetchall()
                if not len(response):
                    return (None, STATUS_MYSQL_ENTRY_NO_EX)
                script = response[0]
                return (script, SUCCESS)
    except Error as e:
        # print(e)
        pass
        
    return (None, ERR_MYSQL_QUERY)