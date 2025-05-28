import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_jwt_secret")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
