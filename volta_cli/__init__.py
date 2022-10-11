# Package variables

__app_name__ = 'volta-cli'
__version__ = '0.1.0'

(
    SUCCESS,
    MYSQL_LOGIN_ERROR,
) = range(2)

ERRORS = {
    MYSQL_LOGIN_ERROR: "[MySQL login error]",
}