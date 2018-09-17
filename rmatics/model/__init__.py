from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo


db = SQLAlchemy()
mongo = PyMongo()
redis = FlaskRedis()
