from models.database import Database
from datetime import datetime
from bson import ObjectId
import dateutil.parser
import math

db = Database()
meteorites = db.meteorites

# returns a meteorite matching an id
def get_meteorite(id):
	meteorite = meteorites.find_one({"_id": ObjectId(id)})
	meteorite["_id"] = str(meteorite["_id"])
	return meteorite

# returns all meteorites
def get_all_meteorites():
	data_to_return = []
	for meteorite in meteorites.find():
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

# returns a limited amount of meteorites using query params passed in
def get_all_meteorites_paginated(request_args):
	data_to_return = []
	meteoritePage, page_size = 1, 100
	if request_args.get("meteoritePage"):
		meteoritePage = int(request_args.get("meteoritePage"))
	if request_args.get("meteoriteAmount"):
		meteoriteAmount = int(request_args.get("meteoriteAmount"))
	page_start = (meteoriteAmount * (meteoritePage))
	for meteorite in meteorites.find().skip(page_start).limit(meteoriteAmount):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

# return a limited amount of randomly sampled meteorites using query params passed in
def get_all_meteorites_sampled(request_args):
	data_to_return = []
	meteoriteAmount = 100
	if request_args.get("meteoriteAmount"):
		meteoriteAmount = int(request_args.get("meteoriteAmount"))
	for meteorite in meteorites.aggregate([{ "$sample": { "size": meteoriteAmount } }]):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

# returns a limited filter list of randomly sampled meteorites using query params passed in
def get_meteorites_with_filter_options_sampled(filter_args):
	data_to_return = []
	meteoriteAmount = 100
	if filter_args.get("meteoriteAmount"):
		meteoriteAmount = int(filter_args.get("meteoriteAmount"))
	filters = get_filter_options(filter_args)

	# Uses the filters from get_filter_options to query the meteorite collection 
	# then randomly samples using the meteorite amount
	for meteorite in meteorites.aggregate([{ "$match": filters  },{ "$sample": { "size": meteoriteAmount } }]):
		meteorite["_id"] = str(meteorite["_id"])
		data_to_return.append(meteorite)
	return data_to_return

# using the query args passed in, returns a dictionary of filters
def get_filter_options(filter_args):
	filters = {}
	if filter_args.get("name"):
		filters["name"] = filter_args.get("name")
	if filter_args.get("classification"):
		filters["recclass"] = filter_args.get("classification")
	if filter_args.get("fall"):
		filters["fall"] = filter_args.get("fall")
	if filter_args.get("mass"):
		# Filters for masses greater than the given mass
		filters["mass (g)"] = {"$gt": int(filter_args.get("mass"))}
	if filter_args.get("startDate") and filter_args.get("endDate"):
		# Removes null years and returns dates inbetween the start date and end date
		filters["year"] = {"$ne": ''}
		filters["$and"] = [{
			"$expr": {
				"$gt": [{ "$dateFromString": { "dateString": "$year" }}, dateutil.parser.parse(filter_args.get("startDate")) ]
			}},
			{"$expr": {
				"$lt": [{ "$dateFromString": { "dateString": "$year" }}, dateutil.parser.parse(filter_args.get("endDate")) ]
			}}]
	if filter_args.get("lat") and filter_args.get("lng") and filter_args.get("radius"):
		# merge the dictionary with the one created in get_filter_for_geolocation_radius
		filters = {**filters, **get_filter_for_geolocation_radius(float(filter_args.get("lat")), float(filter_args.get("lng")), float(filter_args.get("radius")))}

	return filters

# returns a dictionary of filters for the geolocation of meteorites
def get_filter_for_geolocation_radius(lat, lng, radius):
	# Assume radius is in kilometres
	# Calculate the maximum change of lat and lng given a radius
	# Note that every degree of latitude is roughly 111.1 km
	deltaLat = radius / 111.1
	
	# lng is dependent on the latitude so the following formula is used to calculate it
	longintudeDegree = 111.320 * math.cos(lat / 180 * math.pi)

	deltaLng = radius / longintudeDegree

	# calculate upper bounds and lower bounds of lat and lng for a radius
	minLat = lat - deltaLat
	maxLat = lat + deltaLat
	minLng = lng - deltaLng
	maxLng = lng + deltaLng

	filters = {}
	filters["reclat"] = {"$lte": maxLat, "$gte": minLat}
	filters["reclong"] = {"$lte": maxLng, "$gte": minLng}
	return filters

def get_count_of_all_meteorites():
	return meteorites.find().count()