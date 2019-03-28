import os


def bool_(v: str = None) -> bool:
    """Cast bool string representation into actual Bool type
    
    :param v: String, representing bool, e.g. 'True', 'yes'
    :return: Boolean cast result
    """
    if type(v) is bool:
        return v
    if isinstance(v, str) is False:
        return False
    return v.lower() in ('yes', 'true', 't', '1')


class BaseConfig:
    # global
    DEBUG = False
    TESTING = False

    # secrets
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')

    # databases
    URL_ENCODER_ALPHABET = os.getenv('URL_ENCODER_ALPHABET', 'abcdefg')

    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://user:pass@localhost/test')
    MONGO_CONNECT = bool_(os.getenv('MONGO_CONNECT', False))

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
                                        'mysql+pymysql://root:@localhost:3306/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600

    REDIS_URL = os.getenv('REDIS_URL', 'redis://@localhost:6379/0')

    # services
    EJUDGE_NEW_CLIENT_URL = os.getenv('EJUDGE_NEW_CLIENT_URL', 'http://localhost/cgi-bin/new-client')
    EJUDGE_USER = os.getenv('EJUDGE_USER', 'user')
    EJUDGE_PASSWORD = os.getenv('EJUDGE_PASSWORD', 'pass')

    CENTRIFUGO_URL = os.getenv('CENTRIFUGO_URL', 'http://localhost:1377')
    CENTRIFUGO_API_KEY = os.getenv('CENTRIFUGO_API_KEY', 'foo')


class DevConfig(BaseConfig):
    ...


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = False


class ProdConfig(BaseConfig):
    SQLALCHEMY_ECHO = False
