import pymongo
from pymongo import MongoClient
from singleton_decorator import singleton


@singleton
class DBM():
    def __init__(self, db):
        """
        DBM 생성자, dbname을 인자로 받는다.
        :param db: str - database name
        """
        self.mongo = MongoClient()

    def get_db(self, dbname):
        """
        return db object
        :param dbname: str - database name
        :return: db object
        """
        return self.mongo.get_database(dbname)
