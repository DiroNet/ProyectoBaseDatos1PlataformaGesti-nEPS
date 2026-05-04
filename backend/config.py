import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-hospital-2026'
    
    # PostgreSQL Configuration (tu base de datos local)
    DB_NAME = 'ClaseLunesPruebasSoftware'
    DB_USER = 'postgres'
    DB_PASSWORD = '12345'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-hospital-2026'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}