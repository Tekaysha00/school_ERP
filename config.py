import datetime

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///school.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)



