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
keychain: Collection = db["keychain"]

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
	try:
		precheck = tracksToCheckLater.find({"trackData.id": amTrack.amData.get("id")})
		if len(list(precheck)) > 0:
			print(f"Album with ID {amTrack.amData.get('id')} is already in checkLater queue")
			return
	except:
		print("Couldn't properly check for this data's ID in checkLater:\n",amTrack.amData)
	
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
		tracks.append(Album(amData=track["trackData"]))
		print(track["trackData"])

	tracksToCheckLater.delete_many(query)
	print("Checked later tracks: ", len(tracks))

	return tracks


# KEYCHAIN STUFF
appleMusicUserTokenFilter = {"key": "appleMusicUserToken"}
deezerUserTokenFilter = {"key": "deezerUserToken"}
def setUserTokens(appleMusic,deezerToken):
	# print("received tokens: ", appleMusic, deezerToken)
	keychain.update_one(appleMusicUserTokenFilter, {"$set": {"value": (appleMusic if appleMusic != None else "")}}, upsert=True)
	keychain.update_one(deezerUserTokenFilter, {"$set": {"value": (deezerToken if deezerToken != None else "")}}, upsert=True)

def getUserTokens():
	amResult, dResult = keychain.find_one(appleMusicUserTokenFilter), keychain.find_one(deezerUserTokenFilter)
	am, dz = amResult.get("value") if amResult is not None else "", dResult.get("value") if dResult is not None else ""
	return am if am != "" else None, dz if dz != "" else None