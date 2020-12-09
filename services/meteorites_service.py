# from math import radians, cos, sin, asin, sqrt
from models.database import Database
from datetime import datetime
import dateutil.parser

db = Database()
meteorites = db.meteorites

def getAllMeteoritesPaginated(page_size, page_start):
	data_to_return = []
	for meteorite in meteorites.find().skip(page_start).limit(page_size):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

def getMeteoritesWithFilterOptionsPaginated(filter_args, page_size, page_start):
	data_to_return = []
	filters = {}
	print(filter_args)
	if filter_args.get("name"):
		filters["name"] = filter_args.get("name")
	if filter_args.get("classification"):
		filters["recclass"] = filter_args.get("classification")
	if filter_args.get("mass"):
		filters["mass (g)"] = {"$gt": int(filter_args.get("mass"))}
	if filter_args.get("startDate") and filter_args.get("endDate"):
		filters["year"] = {"$ne": ''}
		filters["$and"] = [{
			"$expr": {
				"$gt": [{ "$dateFromString": { "dateString": "$year" }}, dateutil.parser.parse(filter_args.get("startDate")) ]
			}},
			{"$expr": {
				"$lt": [{ "$dateFromString": { "dateString": "$year" }}, dateutil.parser.parse(filter_args.get("endDate")) ]
			}}]

	for meteorite in meteorites.find(filters).skip(page_start).limit(page_size):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return
