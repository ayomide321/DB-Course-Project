import os
from csi3335sp2022 import sql_config
basedir = os.path.abspath(os.path.dirname(__file__))


URI = 'mysql+pymysql://' + sql_config['user'] + ":" + sql_config['password'] + "@" + sql_config['location'] + "/" + sql_config['database']
class Config(object):
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_NAME = sql_config['admin_username']


