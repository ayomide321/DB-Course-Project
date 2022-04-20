import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:omolewa@localhost/baseball'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
