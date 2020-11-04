from flask import Blueprint, make_response, jsonify, request
from pymongo import MongoClient
from models.database import Database
from services.auth_service import jwt_required, get_auth_token
import yaml
import bcrypt
import jwt
import datetime

# TODO ensure duplicate usernames can't exist
# TODO seperate logic in user service

user_controller = Blueprint("users", __name__)
config = yaml.safe_load(open("./config.yml"))
db = Database()
users = db.users
blacklist = db.blacklist


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
			else:
				return make_response(jsonify({'message': 'Bad Passowrd'}, 401))
		return make_response(jsonify({"token": token.decode("UTF-8"), "expiresIn": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}), 200)
	return make_response("Could not verify", 401,{'WWW-Authenticate' : 'Basic realm = "Login required"'})

@user_controller.route('/logout', methods=["POST"])
@jwt_required
def logout():
	auth_token = get_auth_token()
	if not auth_token:
		return make_response(jsonify({'message' : 'Token is missing'}), 401)
	else:
		blacklist.insert_one({"token": auth_token})
	return make_response(jsonify({'message' : 'Logout successful'}), 200)