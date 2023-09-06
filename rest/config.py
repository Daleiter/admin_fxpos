class Config:
    """Plese change configuration for prod ;)"""
    """Default configuration"""
    DEBUG = False
    SERVER_NAME = 'localhost'
    MYSQL_USER = 'db_admin'
    MYSQL_PASSWORD = 'Qq123456'
    POSTGRES_HOST = 'localhost'
    DB_NAME = 'db_company'
    SQLALCHEMY_DATABASE_URI = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}' \
                              f'@{MYSQL_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    """Development configuration"""
    DEBUG = False