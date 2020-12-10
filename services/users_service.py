from flask import Flask, make_response, jsonify, request
from pymongo import MongoClient
from models.database import Database
from bson import ObjectId
import jwt
import yaml

db = Database()
users = db.users

def get_user_id_from_username(username):
	for user in users.find():
		if user["username"] == username:
			return str(user["_id"])
	return ""

def get_all_favourites_for_user_id(user_id):
	user = users.find_one({"_id": ObjectId(user_id)})
	favourites_to_return = []
	for favourite in user["favourites"]:
		favourites_to_return.append(str(favourite))
	return favourites_to_return

def update_favourites_for_user_id(user_id, meteorite_id):
	user = users.find_one({"_id": ObjectId(user_id)})
	for favourite in user["favourites"]:
		if favourite == ObjectId(meteorite_id):
			users.update_one({"_id": ObjectId(user_id)}, {"$pull": {"favourites": ObjectId(meteorite_id)}})
			return "removed existing favourite with identical meteorite_id"
	users.update_one({"_id": ObjectId(user_id)}, {"$push": {"favourites": ObjectId(meteorite_id)}})
	return "favourite added"