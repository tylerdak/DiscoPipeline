import datetime
import time
from Song import Album
from dbstuff import syncLogs
import json
import requests

class AMController:

	# change if user library is on a different storefront
	storefrontCode = 'us'
	standardHeaders = {}
	standardParams = {
		"limit": 1,
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
	
	def parseAlbumsFromResponse(responseDict: dict, dateMinimum):
		albumsArr = []

		for song in responseDict.get("data"):
			
			thisAlbum = Album(song)
			
			if thisAlbum.dateAdded > dateMinimum:
				albumsArr.append(thisAlbum)
			else:
				print(f"end of list (next was {str(thisAlbum.dateAdded)})")
				# returns results + whether or not the limit was reached
				return albumsArr, True
		
		return albumsArr, False
	
	def getAllLibrarySongs(userToken, devToken):

		albumsArr: list[Album] = []

		AMController.standardHeaders = {
			"Authorization": f"Bearer {devToken}",
			'Music-User-Token': userToken
		}

		lastDate = (datetime.datetime.now() - datetime.timedelta(days=15)).date()

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
		responseDict = json.loads(response.content)
		next_url = responseDict.get("next")

		albumsArrAdd, dateLimitReached = AMController.parseAlbumsFromResponse(responseDict,lastDate)
		albumsArr += albumsArrAdd

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
			responseDict = json.loads(response.content)
			next_url = responseDict.get("next")

			albumsArrAdd, dateLimitReached = AMController.parseAlbumsFromResponse(responseDict,lastDate)
			albumsArr += albumsArrAdd

			# update rate limiting variables
			requests_made += 1
			last_request_time = time.time()
		
		print("Count: ",len(albumsArr))
		for album in albumsArr:
			print(f"Date: {album.dateAdded}\nTitle: {album.title}\nArtist: {album.artistName}\n\n")
		




# class AppleMusic(applemusicpy.AppleMusic):





# 	def searchLibrary(self, term, l=None, limit=None, offset=None, types=None, hints=False, os='linux'):
# 		"""
# 		Query the Apple Music API based on a search term

# 		:param term: Search term
# 		:param storefront: Apple Music store front
# 		:param l: The localization to use, specified by a language tag. Check API documentation.
# 		:param limit: The maximum amount of items to return
# 		:param offset: The index of the first item returned
# 		:param types: A list of resource types to return (e.g. songs, artists, etc.)
# 		:param hints: Include search hints
# 		:param os: Operating System being used. If search isn't working on Windows, try os='windows'.

# 		:return: The search results in JSON format
# 		"""
# 		url = self.root + 'me/library/search'
# 		if hints:
# 			url += '/hints'
# 		term = re.sub(' +', '+', term)
# 		if types:
# 			type_str = ','.join(types)
# 		else:
# 			type_str = None

# 		if os == 'linux':
# 			return self._get(url, term=term, l=l, limit=limit, offset=offset, types=type_str)
# 		elif os == 'windows':
# 			params = {
# 				'term': term,
# 				'limit': limit,
# 				'offset': offset,
# 				'types': type_str
# 			}

# 			# The params parameter in requests converts '+' to '%2b'
# 			# On some Windows computers, this breaks the API request, so generate full URL instead
# 			param_string = '?'
# 			for param, value in params.items():
# 				if value is None:
# 					continue
# 				param_string = param_string + str(param) + '=' + str(value) + '&'
# 			param_string = param_string[:len(param_string) - 1]  # This removes the last trailing '&'

# 			return self._get(url + param_string)
# 		else:
# 			return None