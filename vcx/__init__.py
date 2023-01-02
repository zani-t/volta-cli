# Package variables

from typing import NamedTuple

class Login():
    args = {
        "host" : "localhost",
        "user" : "root",
    }
    def __init__(self, **kwargs):
        self.args.update(kwargs)

class DatasetResponseSQL(NamedTuple):
    ds_address: str
    location: bool
    response: int

class DatasetResponsePy(NamedTuple):
    data: str
    response: int

class LoginResponse(NamedTuple):
    login: Login
    response: int

class IDResponse(NamedTuple):
    id: int
    response: int

class RawResponse(NamedTuple):
    output: str
    response: int

class ScriptResponse(NamedTuple):
    script: str
    response: int

class ModelResponse(NamedTuple):
    script: str
    response: int

__app_name__ = 'volta-cli'
__version__ = '0.1.0'

(
    SUCCESS,
    ERR_CONFIG_WRITE,
    ERR_CONFIG_DIR,
    ERR_CONFIG_FILE,
    STATUS_CONFIG_FILE_NO_EX,
    ERR_MYSQL_CONN,
    ERR_MYSQL_DB,
    ERR_MYSQL_QUERY,
    ERR_PANDAS_READ,
    STATUS_MYSQL_DB_EX,
    STATUS_MYSQL_DB_NO_EX,
    STATUS_MYSQL_PROJ_EX,
    STATUS_MYSQL_PROJ_NO_EX,
    STATUS_MYSQL_ENTRY_EX,
    STATUS_MYSQL_ENTRY_NO_EX,
) = range(15)

ERRORS = {
    ERR_CONFIG_WRITE : "[Config write error]",
    ERR_CONFIG_DIR : "[Config directory error]",
    ERR_CONFIG_FILE : "[Config file error]",
    STATUS_CONFIG_FILE_NO_EX : "[Config file doesn't exist]",
    ERR_MYSQL_CONN : "[MySQL connection error]",
    ERR_MYSQL_DB : "[MySQL database error]",
    ERR_MYSQL_QUERY : "[MySQL query error]",
    ERR_PANDAS_READ : "[Pandas read error]",
    STATUS_MYSQL_DB_EX : "[MySQL database 'volta' exists]",
    STATUS_MYSQL_DB_NO_EX : "[MySQL database 'volta' doesn't exist]",
    STATUS_MYSQL_PROJ_EX : "[MySQL project exists already]",
    STATUS_MYSQL_PROJ_NO_EX : "[MySQL project does not exist]",
    STATUS_MYSQL_ENTRY_EX : "[MySQL given entry exists]",
    STATUS_MYSQL_ENTRY_NO_EX : "[MySQL given entry does not exist]",
}