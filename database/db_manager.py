import pymongo
from pymongo import MongoClient


class DBM():
    def __init__(self):
        self.mongo = MongoClient()

    def get_db(self, dbname):
        return self.mongo.get_database(dbname)

