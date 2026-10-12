
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret')

    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME', 'patient_records')
    DB_PORT = int(os.environ.get('DB_PORT', 27476))
    DB_SSL_MODE = os.environ.get('DB_SSL_MODE', 'REQUIRED')
