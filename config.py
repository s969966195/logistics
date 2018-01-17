# coding=utf-8
import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'logistics'
    FLASKY_MAIL_SUBJECT_PREFIX = '[logistics]'
    FLASKY_MAIL_SENDER = 'logistics <m18251957692_1@163.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or '969966195@qq.com'
    FLASKY_ORDERS_PER_PAGE = 20
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'm18251957692_1@163.com'
    MAIL_PASSWORD = 'xiangmu123'
    DEFAULT_MAIL_SENDER = 'm18251957692_1@163.com'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/logistics.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True


config = {
    'default': DevConfig
}
