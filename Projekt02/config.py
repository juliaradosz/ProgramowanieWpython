import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'basniowy-sekret-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basniowa_biblioteka.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False