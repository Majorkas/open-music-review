import os
# set actual secret key in .env file
SECRET_KEY = os.getenv('SECRET_KEY', 'not-set')
#set db URL in .env file too
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
