import datetime
import json
import time

import requests
import tqdm

from Song import Album

class DeezerController:
	token: str = None
	
	def __init__(self, deezerToken: str) -> None:
		self.token = deezerToken
	
	def getUserID(self):
		userAPI = "https://api.deezer.com/user/me"

		if self.token is None:
			return None
		else:
			response = requests.get(userAPI, 
				params = {
					"access_token": self.token
				}
			)

			try:
				responseDict = json.loads(response.content)
				return responseDict.get("id")
			except ValueError:
				return None
			
	def createPlaylist(self,title=None):
		if self.token is None:
			return None
		userID = self.getUserID()
		if userID is None:
			return None
		else:
			playlistAPI = f"https://api.deezer.com/user/{userID}/playlists"

			response = requests.post(playlistAPI, 
		 		params = {
					"access_token": self.token,
					"title": title if title is not None else f'discoPipeline_{datetime.datetime.now().isoformat().replace(" ","_").replace(":","-")}'
				}
			)

			try:
				responseDict = json.loads(response.content)
				return responseDict.get("id")
			except ValueError:
				return None

	# this function will return a dict, because it's easier to use
	# 	when we have multiple outputs we may want
	def addTracksToPlaylist(self, tracklist: list[Album]):

		print(f"I have {len(tracklist)} tracks to add to the playlist. I can only do 50 at a time, so I'll be splitting them up into {int(len(tracklist)/50)+1} batches.")

		if self.token is None:
			return {"code":401, "error":"I can't function without a token, dumbass"}
		else:
			rejectTracks: list[Album] = []

			# rate limiting groundwork
			requests_made = 0
			last_request_time = None
			rate_limit = 50
			# timeframe in seconds
			rate_timeframe = 5


			# deezer can only have 2000 tracks in a single playlist, so we need to create our own
			playlistMaximum = 2000
			playlistBatches = [tracklist[i:i+playlistMaximum] for i in range(0,len(tracklist), playlistMaximum)]
			numPlaylists = len(playlistBatches)
			playlists = []

			for i in range(numPlaylists):
				thisID = self.createPlaylist()
				if thisID is not None:
					playlists.append(thisID)
				else:
					print("THIS SHIT CRASHED AND I DON'T FEEL LIKE COMING UP WITH AN EXIT STRATEGY")
					print("5/0")

			if len(playlistBatches) != len(playlists):
				print("RUH ROH SOME CALCULATION WENT WRONG BECAUSE THE NUMBER OF PLAYLIST IDs DOESN'T MATCH THE NUMBER OF PLAYLIST BATCHES")

			for i,playlistBatch in tqdm.tqdm(enumerate(playlistBatches),desc="Playlist Batches: "):

				playlistID = playlists[i]

				# playlist API can only take 50 tracks at a time. 
				batch_size = 50
				track_id_batches = [playlistBatch[i:i+batch_size] for i in range(0, len(playlistBatch), batch_size)]

				for bi, batch in tqdm.tqdm(enumerate(track_id_batches),desc="Track Batches: "):
					# rate limit self while requesting API
					if requests_made >= rate_limit and last_request_time is not None:
						time_since_last_request = time.time() - last_request_time
						if time_since_last_request < rate_timeframe:
							time_to_wait = rate_timeframe - time_since_last_request
							tqdm.tqdm.write(f"[{datetime.datetime.now().time()}]: Sleeping...")
							time.sleep(time_to_wait)
							tqdm.tqdm.write(f"[{datetime.datetime.now().time()}]: Awoken!")
							requests_made = 0
							last_request_time = None

					# these are batches of Album objects marked as tracks,
					# NOT track ids
					# We must convert them each to track ids first
					trackIDList = map(lambda x: str(x.deezer_ID),batch)

					api_url = f"https://api.deezer.com/playlist/{playlistID}/tracks"
					params = {
						"access_token": self.token,
						"songs": ','.join(trackIDList)
					}

					response = requests.post(api_url,params=params)

					# update rate limiting variables
					requests_made += 1
					last_request_time = time.time()

					try:
						responseDict = json.loads(response.content)
						responseError = responseDict.get("error") 
					except ValueError:
						responseError = { "code": 408, "message": f"Unable to unpack response.content: {response.content}", "type": "DictUnpackError"}
					except AttributeError:
						if type(responseDict) == bool:
							responseError = None
						else:
							responseError = { "code": 409, "message": f"Unable to unpack response.content: {response.content}", "type": "DictUnpackError"}

					if responseError is not None:
						code = responseError.get("code")
						message = responseError.get("message")
						typed = responseError.get("type")

						if typed == "ParameterException":
							tqdm.tqdm.write(f"No new tracks in batch {bi}...")
						else:
							tqdm.tqdm.write(f"\nUnhandled Error Type (Batch {bi}): {typed}")
							tqdm.tqdm.write(f"Details: [Error {code}]: {message}\n")
							
							rejectTracks += batch
					else:
						tqdm.tqdm.write(f"Batch {bi} passed.")
			
			if len(rejectTracks) == 0:
				return {
					"code":200,
					"message":"No reject tracks found.",
					"playlists": playlists
				}
			elif len(rejectTracks) == len(tracklist):
				return {
					"code": 400,
					"message": "All tracks attempted were rejected. Seems likely that the playlist IDs are invalid.",
					"rejectTracks": rejectTracks,
					"playlists": playlists
				}
			else:
				return {
					"code": 300,
					"message": f"{len(rejectTracks)} tracks failed to convert.",
					"rejectTracks": rejectTracks,
					"playlists": playlists
				}
