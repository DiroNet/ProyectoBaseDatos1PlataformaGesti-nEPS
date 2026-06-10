import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-eps-bienestar-2026'
    
    # MySQL Configuration (MySQL Workbench)
    DB_NAME = 'eps_salud'
    DB_USER = 'root'
    DB_PASSWORD = 'admin1234'
    DB_HOST = 'localhost'
    DB_PORT = '3306'
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    
    # JWT Configuration // encriptar
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-eps-bienestar-2026-secure-token'
    JWT_ACCESS_TOKEN_EXPIRES = 86400

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}