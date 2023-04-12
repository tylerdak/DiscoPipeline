import datetime
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
from typing import Type

import pytz

from Song import Album

client = MongoClient("mongo")

db = client["DiscoPipeline"]

# declare each collection below
# [symbol_name]: Collection = db["[matching_symbol_name_hopefully]"]

syncLogs: Collection = db["syncLogs"]
tracksToCheckLater: Collection = db["checkLater"]

def insertSyncLog(errorFlags, null=False):
	syncLogs.insert_one({
		"datestamp":f"{datetime.datetime.now().replace(tzinfo=pytz.utc)}",
		
		# this error flags property is saved so the person investigating the logs can go back and see what error logs to check
		"errorFlags": errorFlags,
		"null": null
	})

def lastSync():
	query = {"null": False}
	sort = [('datestamp', DESCENDING)]
	result = syncLogs.find_one(query, sort=sort)
	if result is None:
		return None
	
	datestampStr = result.get("datestamp")
	if datestampStr is not None:
		try:
			datestamp = datetime.datetime.fromisoformat(datestampStr)
		except:
			datestamp = None
	else:
		datestamp = None
	return datestamp
		
def checkLater(amTrack: Album):
	tracksToCheckLater.insert_one({
		"datestamp":amTrack.releaseDate,
		"trackData": amTrack.amData
	})
	
def check():
	currTime = datetime.datetime.now()
	query = {"datestamp": {'$lt': currTime}}
	results = tracksToCheckLater.find(query)
	
	tracks: list[Album] = []
	
	for track in results:
		track.append(Album(amData=results["trackData"]))
		print(results["trackData"])

	tracksToCheckLater.delete_many(query)
	print("Checked later tracks: ", len(tracks))

	return tracks
