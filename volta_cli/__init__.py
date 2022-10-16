# Package variables

from typing import NamedTuple

class Login():
    args = {
        "host" : "localhost",
        "user" : "root",
    }
    def __init__(self, **kwargs):
        self.args.update(kwargs)

class LoginResponse(NamedTuple):
    login: Login
    response: int

__app_name__ = 'volta-cli'
__version__ = '0.1.0'

(
    SUCCESS,
    ERR_CONFIG_WRITE,
    ERR_CONFIG_DIR,
    ERR_CONFIG_FILE,
    ERR_MYSQL_CONN,
    ERR_MYSQL_DB,
    STATUS_MYSQL_DB_EX
) = range(7)

ERRORS = {
    ERR_CONFIG_WRITE : "[Config write error]",
    ERR_CONFIG_DIR : "[Config directory error]",
    ERR_CONFIG_FILE : "[Config file error]",
    ERR_MYSQL_CONN : "[MySQL connection error]",
    ERR_MYSQL_DB : "[MySQL database error]",
    STATUS_MYSQL_DB_EX : "[MySQL database 'volta' exists]",
}