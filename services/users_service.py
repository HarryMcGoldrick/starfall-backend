from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from models.database import Database
import jwt
import yaml

db = Database()
users = db.users

def get_user_id_from_username(username):
    for user in users.find():
        if user["username"] == username:
            return str(user["_id"])
        else:
            return False
