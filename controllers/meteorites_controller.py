from flask import Blueprint, make_response, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from services.users_service import get_user_id_from_username, update_favourites_for_user_id, get_all_favourites_for_user_id
from services.auth_service import jwt_required
from models.database import Database
from services.meteorites_service import (get_all_meteorites_sampled, get_meteorites_with_filter_options_sampled,
get_all_meteorites, get_all_meteorites_paginated, get_count_of_all_meteorites, get_meteorite)

meteorite_controller = Blueprint("meteorites", __name__)
db = Database()
meteorites = db.meteorites
users = db.users

# Returns a full list of unique meteorite classifications
@meteorite_controller.route("/meteorites/classifications", methods=["GET"])
def get_all_meteorite_classifications():
	classification = []
	meteorites = get_all_meteorites()
	for meteorite in meteorites:
		if meteorite["recclass"]:
			if meteorite["recclass"] not in classification:
				classification.append(meteorite["recclass"])
	return make_response(jsonify(classification), 200)

# Returns a random sample of meteorites
@meteorite_controller.route("/meteorites", methods=["GET"])
def get_all_meteorites_with_sampling():	
	meteorites = get_all_meteorites_sampled(request.args)
	return make_response(jsonify(meteorites), 200)

# Returns a paginated array of meteorites
@meteorite_controller.route("/meteorites/paginated", methods=["GET"])
def get_meteorites_paginated():	
	meteorites = get_all_meteorites_paginated(request.args)
	return make_response(jsonify(meteorites), 200)

# Returns a random sample of meteorites matching the filters in the query params
@meteorite_controller.route("/meteorites/filter", methods=["GET"])
def get_all_meteorites_filtered():
	meteorites = get_meteorites_with_filter_options_sampled(request.args)
	return make_response(jsonify(meteorites), 200)

# returns a singular meteorite
@meteorite_controller.route("/meteorites/<id>", methods=["GET"])
def get_single_meteorite(id):
	meteorite = get_meteorite(id)
	return make_response(jsonify(meteorite), 200)

# returns the total number of records in the meteorite db
@meteorite_controller.route("/meteorites/count", methods=["GET"])
def get_meteorite_count():
	count = get_count_of_all_meteorites()
	return make_response(jsonify(count), 200)

# returns all the meteorite ids that are stored in user favourites
@meteorite_controller.route("/meteorites/favourites", methods=["GET"])
@jwt_required
def get_all_favourites_for_user():
	if not request.args.get("username"):
		return make_response(jsonify({"error": "invalid request"}), 400)
	user_id = get_user_id_from_username(request.args.get("username"))
	if not user_id:
		return make_response(jsonify({"error": "username invalid or does not exist"}), 400)
	favourites = get_all_favourites_for_user_id(user_id)
	return make_response(jsonify(favourites), 200)

# adds a meteorite id to user favourites if it does not exist
# removes a meteorite id in user favourites if it does exist
@meteorite_controller.route("/meteorites/favourites", methods=["POST"])
@jwt_required
def update_favourite():
	if not "meteorite_id" in request.json or not "username" in request.json:
		return make_response(jsonify({"error": "invalid body"}), 400)
	meteorite_id = request.json["meteorite_id"]
	user_id = get_user_id_from_username(request.json["username"])
	responseText = update_favourites_for_user_id(user_id, meteorite_id)
	return make_response(jsonify({"update": responseText}), 200)