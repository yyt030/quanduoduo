# coding: utf-8
import os


class Config(object):
    """配置基类"""
    # Flask app config
    DEBUG = False
    TESTING = False
    SECRET_KEY = "\xb5\xb3}#\xb7A\xcac\x9d0\xb6\x0f\x80z\x97\x00\x1e\xc0\xb8+\xe9)\xf0}"
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    SESSION_COOKIE_NAME = 'weshop_session'

    # Root path of project
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Site domain
    SITE_DOMAIN = "http://localhost:5000"

    # SQLAlchemy config
    # See:
    # https://pythonhosted.org/Flask-SQLAlchemy/config.html#connection-uri-format
    # http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html#database-urls
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/weshop"

    # Sendcloud SMTP config
    SMTP_HOST = "smtpcloud.sohu.com"  # SMTP服务器
    SMTP_PORT = 25
    SMTP_USER = "postmaster@tuomengjiaoyu.sendcloud.org"  # 用户名
    SMTP_PASSWORD = "zNSOP8TOlFxeCt17"  # 口令

    # Redis
    REDIS = False  # 是否启用Redis
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 1
    # Uploadsets config
    UPLOADS_DEFAULT_DEST = "/documents/uploads"  # 上传文件存储路径
    UPLOADS_DEFAULT_URL = "http://localhost/jeepsk_uploads/"  # 上传文件访问URL

    # Flask-DebugToolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Sentry config
    SENTRY_DSN = ''

    # Alipay config
    # 合作身份者ID，以2088开头的16位纯数字
    ALIPAY_PARTNER = ''
    # 安全检验码，以数字和字母组成的32位字符
    ALIPAY_KEY = ''
    # 签约支付宝账号或卖家支付宝帐户
    ALIPAY_SELLER_EMAIL = ''
    # 交易过程中服务器通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    ALIPAY_NOTIFY_URL = 'http://www.jeepsk.com/user/alipay_notify'
    # 付完款后跳转的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    # return_url的域名不能写成http://localhost/js_php_utf8/return_url.php ，否则会导致return_url执行无效
    ALIPAY_RETURN_URL = 'http://www.jeepsk.com/user/pay'
    # 网站商品的展示地址，不允许加?id=123这类自定义参数
    ALIPAY_SHOW_URL = 'http://www.jeepsk.com'
    # 签名方式 不需修改
    ALIPAY_SIGN_TYPE = 'MD5'
    # 字符编码格式 目前支持 GBK 或 utf-8
    ALIPAY_INPUT_CHARSET = 'utf-8'
    # 访问模式,根据自己的服务器是否支持ssl访问，若支持请选择https；若不支持请选择http
    ALIPAY_TRANSPORT = 'http'
    # 单价
    PRICE = 49

    # Host string, used by fabric
    HOST_STRING = "ubuntu@182.254.152.46"

    DEVICES = [
        ('mobile',
         'iPhone|iPod|Android.*Mobile|Windows.*Phone|dream|blackberry|CUPCAKE|webOS|incognito'
         '|webmate'),
        ('tablet', 'iPad|Android'),
        ('pc', '.*')
    ]
