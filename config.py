import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = 'hasini'
    DB_NAME = 'patient_record_management'
