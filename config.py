import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///pingpong_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
