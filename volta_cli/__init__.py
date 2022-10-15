# Package variables

class Login():
    hostname: str = "localhost"
    username: str = "root"
    password: str = None

    def __init__(self, hostname: str, username: str, password: str):
        self.hostname = hostname
        self.username = username
        self.password = password

__app_name__ = 'volta-cli'
__version__ = '0.1.0'

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    CONFIG_WRITE_ERROR,
    MYSQL_CONN_ERROR,
    MYSQL_QUERY_ERROR,
    MYSQL_DATABASE_EXISTS,
) = range(7)

ERRORS = {
    DIR_ERROR : "[Config directory error]",
    FILE_ERROR : "[Config file error]",
    CONFIG_WRITE_ERROR : "[Config write error]",
    MYSQL_CONN_ERROR : "[MySQL connection error]",
    MYSQL_QUERY_ERROR : "[MySQL query error]",
    MYSQL_DATABASE_EXISTS : "[MySQL database 'volta' exists]"
}