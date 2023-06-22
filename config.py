
class Setting:
    # DB관련
    HOST = 'mysqlinstance.cr2sp2mx5gjz.ap-northeast-2.rds.amazonaws.com'
    DATABASE = 'movie_db'
    DB_USER = 'movie_db_user'
    DB_PASSWORD = '1234'

    # DB 비밀번호 SALT
    SALT = '12a345s6df789'

    # JWT
    JWT_SECRET_KEY = 'jwtkey'
    JWT_ACCESS_TOKKEN_EXPIRES = False
    PROPAGATE_EXCEPTIONS = True