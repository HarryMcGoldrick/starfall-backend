# from math import radians, cos, sin, asin, sqrt
from models.database import Database
from datetime import datetime
import dateutil.parser

db = Database()
meteorites = db.meteorites

def getAllMeteorites():
	data_to_return = []
	for meteorite in meteorites.find():
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

def getAllMeteoritesPaginated(request_args):
	data_to_return = []
	page_num, page_size = 1, 100
	if request_args.get("meteoritePage"):
		page_num = int(request.args.get("pn"))
	if request_args.get("meteoriteAmount"):
		page_size = int(request.args.get("meteoriteAmount"))
	page_start = (meteoriteAmount * (meteoritePage - 1))
	for meteorite in meteorites.find().skip(page_start).limit(meteoriteAmount):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

def getAllMeteoritesSampled(request_args):
	data_to_return = []
	meteoriteAmount = 100
	if request_args.get("meteoriteAmount"):
		meteoriteAmount = int(request_args.get("meteoriteAmount"))
	for meteorite in meteorites.aggregate([{ "$sample": { "size": meteoriteAmount } }]):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return


def getMeteoritesWithFilterOptionsSampled(filter_args):
	data_to_return = []
	meteoriteAmount = 100
	if filter_args.get("meteoriteAmount"):
		meteoriteAmount = int(filter_args.get("meteoriteAmount"))
	filters = getFilterOptions(filter_args)
	for meteorite in meteorites.aggregate([{ "$match": filters  },{ "$sample": { "size": meteoriteAmount } }]):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

def getFilterOptions(filter_args):
	filters = {}
	if filter_args.get("name"):
		filters["name"] = filter_args.get("name")
	if filter_args.get("classification"):
		filters["recclass"] = filter_args.get("classification")
	if filter_args.get("fall"):
		filters["fall"] = filter_args.get("fall")
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
	return filters