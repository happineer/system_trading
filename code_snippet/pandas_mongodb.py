import pandas as pd
from pymongo import MongoClient

mongo = MongoClient()
db = mongo.TopTrader
cur = db.day_stat.find({})
data = pd.DataFrame(list(cur))
print(data.head())

