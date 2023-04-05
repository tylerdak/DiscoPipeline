from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Type

client = MongoClient("mongo")

db = client["DiscoPipeline"]

# declare each collection below
# [symbol_name]: Collection = db["[matching_symbol_name_hopefully]"]

syncLogs: Collection = db["syncLogs"]