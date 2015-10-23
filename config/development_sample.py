# coding: utf-8
from .default import Config


class DevelopmentConfig(Config):
    # App config
    DEBUG = True

    # Uploadsets config
    UPLOADS_DEFAULT_DEST = "E:/php/xampp/htdocs/tm_uploads"  # 上传文件存储路径
    UPLOADS_DEFAULT_URL = "http://localhost:8080/tm_uploads/"  # 上传文件访问URL

    # SQLAlchemy config
    # 如果是空密码，则直接将password删除即可
    SQLALCHEMY_DATABASE_URI = "mysql://root@localhost/tm2"

    # Redis config
    REDIS = False
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 1
