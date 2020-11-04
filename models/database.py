from pymongo import MongoClient
import yaml

class Database:
    def __init__(self):
        config = yaml.safe_load(open("./config.yml"))
        self.client = MongoClient(config["database"]["port"])
        self.db = self.client.fsDB
        self.meteorites = self.db.meteorite_landings
        self.users = self.db.users
        self.blacklist = self.db.blacklist
