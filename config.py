 # config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost:5432/user'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
