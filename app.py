from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from auth import jwt_required, get_auth_token
from bson import ObjectId
from users import get_user_id_from_username
import yaml
import bcrypt
import jwt
import datetime

app = Flask(__name__)
CORS(app)
config = yaml.safe_load(open("config.yml"))
secret_key = config["auth"]["secret"]


client = MongoClient(config["database"]["port"])
db = client.fsDB
meteorites = db.meteorite_landings
users = db.users
blacklist = db.blacklist

@app.route("/", methods=["GET"])
def index():
	return make_response("<h1>Star fall!</h1>", 200)

@app.route("/meteorites", methods=["GET"])
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

@app.route("/meteorites/favourites", methods=["GET"])
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

@app.route("/meteorites/favourites", methods=["POST"])
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


# -------------- Login routes ----------------------------------

@app.route("/login", methods=["POST"])
def login():
	if request.data:
		user = users.find_one({'username': request.json["username"]})
		if user is not None:
			if bcrypt.checkpw(bytes(request.json["password"], 'UTF-8'), user["password"]):
				token = jwt.encode({
					'user': request.json["username"],
					'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
				}, secret_key)
			else:
				return make_response(jsonify({'message': 'Bad Passowrd'}, 401))
		return make_response(jsonify({"token": token.decode("UTF-8"), "expiresIn": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}), 200)
	return make_response("Could not verify", 401,{'WWW-Authenticate' : 'Basic realm = "Login required"'})

@app.route('/logout', methods=["POST"])
@jwt_required
def logout():
	auth_token = get_auth_token()
	if not auth_token:
		return make_response(jsonify({'message' : 'Token is missing'}), 401)
	else:
		blacklist.insert_one({"token": auth_token})
	return make_response(jsonify({'message' : 'Logout successful'}), 200)



if __name__ == "__main__":
	app.run(debug=True)