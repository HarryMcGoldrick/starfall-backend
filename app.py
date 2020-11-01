from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from auth import jwt_required
import yaml

app = Flask(__name__)
CORS(app)
config = yaml.safe_load(open("config.yml"))

client = MongoClient(config["database"]["port"])
db = client.fsDB
meteorites = db.meteorite_landings

@app.route("/", methods=["GET"])
def index():
	return make_response("<h1>Hello world!</h1>", 200)

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

if __name__ == "__main__":
	app.run(debug=True)