from flask import Blueprint, make_response, jsonify, request
from pymongo import MongoClient
from models.database import Database
from services.auth_service import jwt_required, get_auth_token
import yaml
import bcrypt
import jwt
import datetime

user_controller = Blueprint("users", __name__)
config = yaml.safe_load(open("./config.yml"))
db = Database()
users = db.users
blacklist = db.blacklist

# Registers a user given a username and password
# Password is hashed before storage
@user_controller.route("/register", methods=["POST"])
def register():
	password = request.json["password"].encode('utf-8')
	salt = bcrypt.gensalt()
	hashed_password = bcrypt.hashpw(password, salt)
	isExisting = users.find_one({'username': request.json["username"]})
	if isExisting is not None:
		return make_response(jsonify({"response": "user already exists"}), 401)
	else:
		users.insert_one({"username": request.json["username"], "password": hashed_password, "favourites": [] })
		return make_response(jsonify({"response": "success user created!"}), 200)

# Returns a jwt token if user credentials are present in the database
@user_controller.route("/login", methods=["POST"])
def login():
	if request.data:
		user = users.find_one({'username': request.json["username"]})
		if user is not None:
			if bcrypt.checkpw(bytes(request.json["password"], 'UTF-8'), user["password"]):
				token = jwt.encode({
					'user': request.json["username"],
					'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
				}, config["auth"]["secret"])
				return make_response(jsonify({"token": token.decode("UTF-8"), "expiresIn": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}), 200)
			else:
				return make_response(jsonify({'message': 'Bad Password'}), 401)
	return make_response("Could not verify", 401,{'WWW-Authenticate' : 'Basic realm = "Login required"'})

# blacklists the given jwt token
@user_controller.route('/logout', methods=["POST"])
@jwt_required
def logout():
	auth_token = get_auth_token()
	if not auth_token:
		return make_response(jsonify({'message' : 'Token is missing'}), 401)
	else:
		blacklist.insert_one({"token": auth_token})
	return make_response(jsonify({'message' : 'Logout successful'}), 200)