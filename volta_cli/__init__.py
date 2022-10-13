from typing import NamedTuple

# Package variables

class Login(NamedTuple):
    hostname: str = "localhost"
    username: str = "root"
    password: str = None

__app_name__ = 'volta-cli'
__version__ = '0.1.0'

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    CONFIG_WRITE_ERROR,
    MYSQL_CONN_ERROR,
) = range(5)

ERRORS = {
    DIR_ERROR : "[Config directory error]",
    FILE_ERROR : "[Config file error]",
    CONFIG_WRITE_ERROR : "[Config write error]",
    MYSQL_CONN_ERROR : "[MySQL connection error]",
}