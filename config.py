import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '984e18a7-8595-4bb4-bcb2-8f530aa8912f'