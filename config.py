import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

import os
import datetime
from libraries import utils
basedir = os.path.abspath(os.path.dirname(__file__))


# configuration global parameters
config_data = {}
if os.environ.get("FLASK_CONFIG", None):
    config_name = os.environ.get("FLASK_CONFIG", "development")
    if config_name.lower().strip() == "development":
        config_data = utils.loadAutoNextPhaseConfigJSON()
    else:
        config_data = utils.loadAutoConfigJSON()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'key which is hard to guess'
    WTF_CSRF_SECRET_KEY = "hard to guess key for wt forms"
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=7)

    AUTO_MAIL_SUBJECT_PREFIX = '[Aututomation-WenUI]'
    AUTO_MAIL_SENDER = 'Auto-WebUI <autotools-dlist@digitalguardian.com>'
    AUTO_ADMIN = os.environ.get('AUTO_ADMIN', None)

    LDAP_PROVIDER_URL = 'ldap://it-dc001.verdasys.com:3268'
    LDAP_PROTOCOL_VERSION = 3

    SESSION_TYPE = "filesystem"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    DEBUG = True

    SQLALCHEMY_DATABASE_URI = \
        "mysql://{user}:{passwd}@{host}.acelab.com/authorization"\
            .format(user=SCHDB_USER, passwd=SCHDB_PASS, host=SCHDB_HOST)
    SQLALCHEMY_BINDS = {
        'schedulerdb': 'mysql://{user}:{passwd}@{host}.acelab.com/Oracle'
            .format(user=SCHDB_USER, passwd=SCHDB_PASS, host=SCHDB_HOST),
        'resourcedb': 'mysql://{user}:{passwd}@{host}/{dbname}'
            .format(user=RESDB_USER, passwd=RESDB_PASS, host=RESDB_HOST, dbname=RESDB_NAME)
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.urandom(50)
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=120)


class TestingConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


cache_config = {
    'CACHE_DEFAULT_TIMEOUT': 300,
    "CACHE_TYPE": "redis",
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,

}
