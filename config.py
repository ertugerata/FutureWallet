import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    # Add other configuration variables here
