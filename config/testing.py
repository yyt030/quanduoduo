# coding: utf-8
from .default import Config


class TestingConfig(Config):
    # App config
    TESTING = True

    # Disable csrf while testing
    WTF_CSRF_ENABLED = False

    # Uploadsets config
    UPLOADS_DEFAULT_DEST = "/Library/WebServer/Documents/tm_uploads"
    UPLOADS_DEFAULT_URL = "http://localhost/js_uploads/"

    # Db config
    SQLALCHEMY_DATABASE_URI = "sqlite:///%s/db/testing.sqlite3" % Config.PROJECT_PATH

    # Redis config
    REDIS = False
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 1
