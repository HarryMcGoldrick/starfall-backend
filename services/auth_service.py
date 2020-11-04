from functools import wraps
from flask import make_response, jsonify, request
from models.database import Database
import jwt
import yaml

config = yaml.safe_load(open("config.yml"))
db = Database()
blacklist = db.blacklist

def jwt_required(func):
	@wraps(func)
	def jwt_required_wrapper(*args, **kargs):
		auth_token = get_auth_token()
		bl_token = blacklist.find_one({"token": auth_token})
		if bl_token is not None:
			return make_response(jsonify( {'message' : 'Token has been cancelled'}), 401)
		if not auth_token:
			return jsonify({"message": "Token is missing"}, 401)
		try:
			data = jwt.decode(auth_token, config["auth"]["secret"])
		except:
			return jsonify({"message": "Token is invalid"}, 401)
		return func(*args, **kargs)
	return jwt_required_wrapper

def get_auth_token():
	auth_header = request.headers.get("Authorization")
	if auth_header:
		auth_token = auth_header.split(" ")[1]
		auth_token = auth_token.replace('"', "")
	else:
		auth_token = ''
	return auth_token