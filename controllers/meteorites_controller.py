from flask import Blueprint, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from services.users_service import get_user_id_from_username
from services.auth_service import jwt_required
from models.database import Database

meteorite_controller = Blueprint("meteorites", __name__)
db = Database()
meteorites = db.meteorites
users = db.users

# TODO seperate logic in meteorite service

@meteorite_controller.route("/meteorites", methods=["GET"])
def get_all_meteorites():
	page_num, page_size = 1, 100
	if request.args.get("pn"):
		page_num = int(request.args.get("pn"))
	if request.args.get("ps"):
		page_size = int(request.args.get("ps"))
	page_start = (page_size * (page_num - 1))
	
	data_to_return = []
	for meteorite in meteorites.find().skip(page_start).limit(page_size):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)

	return make_response(jsonify(data_to_return), 200)

@meteorite_controller.route("/meteorites/favourites", methods=["GET"])
@jwt_required
def get_all_favourites_for_user():
	if not request.args.get("username"):
		return make_response(jsonify({"error": "invalid request"}), 400)
	user_id = get_user_id_from_username(request.args.get("username"))
	if not user_id:
		return make_response(jsonify({"error": "username invalid or does not exist"}), 400)
	user_to_update = users.find_one({"_id": ObjectId(user_id)})
	favourites_to_return = []
	for favourite in user_to_update["favourites"]:
		favourites_to_return.append(str(favourite))
	return make_response(jsonify(favourites_to_return), 200)

@meteorite_controller.route("/meteorites/favourites", methods=["POST"])
@jwt_required
def update_favourite():
	if not "meteorite_id" in request.json or not "username" in request.json:
		return make_response(jsonify({"error": "invalid body"}), 400)
	meteorite_id = request.json["meteorite_id"]
	user_id = get_user_id_from_username(request.json["username"])
	user_to_update = users.find_one({"_id": ObjectId(user_id)})
	for favourite in user_to_update["favourites"]:
		if favourite == ObjectId(meteorite_id):
			users.update_one({"_id": ObjectId(user_id)}, {"$pull": {"favourites": ObjectId(meteorite_id)}})
			return make_response(jsonify({"update": "removed existing favourite with identical meteorite_id"}), 200)
	users.update_one({"_id": ObjectId(user_id)}, {"$push": {"favourites": ObjectId(meteorite_id)}})
	return make_response(jsonify({"update": "favourite added"}), 200)