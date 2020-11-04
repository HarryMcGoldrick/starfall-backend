from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
import jwt
import yaml

config = yaml.safe_load(open("config.yml"))
secret_key = config["auth"]["secret"]
client = MongoClient(config["database"]["port"])
db = client.fsDB
users = db.users

def get_user_id_from_username(username):
    for user in users.find():
        if user["username"] == username:
            return str(user["_id"])
        else:
            return False
