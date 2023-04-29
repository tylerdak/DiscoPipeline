import datetime
import time
from Song import Album
import dbstuff
import json
import requests
import pytz

class AMController:

	# change if user library is on a different storefront
	storefrontCode = 'us'
	standardHeaders = {}
	standardParams = {
		# "limit": 1,
		"include": "catalog",
		"sort": "-dateAdded"
	}

	root_api = 'https://api.music.apple.com'
	def endpoint_allLibraryAlbums(withOffset: int = 0):
		return f'https://api.music.apple.com/v1/me/library/albums?offset={withOffset}'
	def endpoint_oneLibrarySong(songID):
		return 'https://api.music.apple.com/v1/me/library/songs/' + str(songID)
	def endpoint_oneCatalogSong(songID):
		return f'https://api.music.apple.com/v1/catalog/{AMController.storefrontCode}/songs/' + str(songID)
	
	personalUploads: list[dict] = []
	
	def parseAlbumsFromResponse(responseDict: dict, dateMinimum):
		albumsArr = []
		

		print("Parsing and filtering albums...")

		for song in responseDict.get("data"):
			
			# don't collect this song if it's a personal upload
			catData = song.get("relationships").get("catalog").get("data")
			if len(catData) == 0 or catData[0].get("attributes") == None:
				AMController.personalUploads.append(song)
				continue

			thisAlbum = Album(song)

			if thisAlbum.releaseDate > datetime.datetime.now():
				# save this album for later instead, it comes out on a future date,
				# and likely won't be on deezer until then.
				print("Skipping unreleased album: ", thisAlbum.title, thisAlbum.artistName, thisAlbum.releaseDate)
				dbstuff.checkLater(thisAlbum)
				continue
			print("\n\n")
			print(f"thisAlbum: {thisAlbum.artistName} - {thisAlbum.title}")
			print(f"thisAlbum.dateAdded: {thisAlbum.dateAdded.date()}")
			print(f"dateMinimum: {dateMinimum.date()}")
			if thisAlbum.dateAdded.date() >= dateMinimum.date():
				albumsArr.append(thisAlbum)
			else:
				# print(f"end of list (next was {str(thisAlbum.dateAdded)})")
				# returns results + whether or not the limit was reached
				print("Reached end of list, moving on...")	
				return albumsArr, True
		
		print("Limit not reached, there's more to get.")
		return albumsArr, False
	
	def getAllLibrarySongs(userToken, devToken, log_folder):

		albumsArr: list[Album] = []

		AMController.standardHeaders = {
			"Authorization": f"Bearer {devToken}",
			'Music-User-Token': userToken
		}

		lastDate = dbstuff.lastSync()

		if lastDate is None:
			print("no previous sync found, getting all music...")
			lastDate = datetime.datetime.fromisoformat("2001-06-21").replace(tzinfo=pytz.utc)

		# rate limiting groundwork
		requests_made = 0
		last_request_time = None
		rate_limit = 20
		# timeframe in seconds
		rate_timeframe = 60

		response = requests.get(AMController.endpoint_allLibraryAlbums(),
	       	params=AMController.standardParams,
			headers=AMController.standardHeaders
		)
		try:
			responseDict = json.loads(response.content)
			next_url = responseDict.get("next")
		except ValueError:
			print("oh god oh fuck: ", response.content)
			next_url = None

		albumsArrAdd, dateLimitReached = AMController.parseAlbumsFromResponse(responseDict,lastDate)
		albumsArr += albumsArrAdd

		albumsArr += dbstuff.check()

		while next_url is not None and not dateLimitReached:
			# Check if rate limit has been reached
			if requests_made >= rate_limit and last_request_time is not None:
				time_since_last_request = time.time() - last_request_time
				if time_since_last_request < rate_timeframe:
					time_to_wait = rate_timeframe - time_since_last_request
					print(f"[{datetime.datetime.now().time()}]: Sleeping...")
					time.sleep(time_to_wait)
					print(f"[{datetime.datetime.now().time()}]: Awoken!")
					requests_made = 0
					last_request_time = None
			
			# make next request
			response = requests.get(
				AMController.root_api + next_url,
			   	params=AMController.standardParams,
				headers=AMController.standardHeaders
			)
			try:
				responseDict = json.loads(response.content)
				next_url = responseDict.get("next")
			except ValueError:
				print("ah darn oh no")
				next_url = None

			albumsArrAdd, dateLimitReached = AMController.parseAlbumsFromResponse(responseDict,lastDate)
			albumsArr += albumsArrAdd

			# update rate limiting variables
			requests_made += 1
			last_request_time = time.time()
		
		if len(AMController.personalUploads) != 0:
			Album.exportPersonalUploads(AMController.personalUploads, log_folder=log_folder)
			AMController.personalUploads = []

		print("Album Count: ",len(albumsArr))

		albumsExportable = Album.exportList(albumsArr)
		return albumsArr

		# dbstuff.insertSyncLog(albumsExportable)
		