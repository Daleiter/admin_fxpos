class Config:
    SECRET_KEY = 'default_secret_key'
    JWT_SECRET_KEY = 'your-secret-key'
    JSON_AS_ASCII = False
    RESTFUL_JSON = {
        'ensure_ascii': False
    }
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:inventory_atadgp@192.168.1.15:5432/db_inventory'
    SQLALCHEMY_BINDS = {
        'cashdesk_db': 'postgresql://sysdba:masterkey@192.168.1.172:5432/dbmain',
        'guac_db': 'postgresql://postgres:inventory_atadgp@192.168.1.15:5432/guacamole_db'
    }
    REDIS_URL = 'redis://192.168.1.15'
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = 'redis://192.168.1.15:6379/0'
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    # Other development configuration options


class ProductionConfig(Config):
    SECRET_KEY = 'secure_secret_key'
    # Other production configuration options
