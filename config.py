import os
from dotenv import load_dotenv

load_dotenv()


class Configuration(object):
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY')

    # PostgreSQL config
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False