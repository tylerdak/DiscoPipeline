
import datetime
import json
import time
import tqdm

import requests

from Song import Album


class ConversionController:
	endpoint = "https://api.song.link/v1-alpha.1/links"
	
	endpoint_params = {
		'userCountry': 'US',
		'songIfSingle': 'true'
		# you must pass in the url param yourself
	}

	

	def paramsWith(url):
		temp = ConversionController.endpoint_params.copy()
		temp.update({ 'url': url })
		return temp
	
	def addDeezerLinks(albums: list[Album]):
		print("Beginning conversion to Deezer links...")

		# rate limiting groundwork
		requests_made = 0
		last_request_time = None
		rate_limit = 10
		# timeframe in seconds
		rate_timeframe = 60

		# should return a list of the albums that the API failed to retrieve
		rejectAlbums: list[Album] = []

		successAlbums: list[Album] = []

		for album in tqdm.tqdm(albums):
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
			
			# make next request
			response = requests.get(
				ConversionController.endpoint,
			   	params=ConversionController.paramsWith(album.am_storeURL)
			)

			# update rate limiting variables
			requests_made += 1
			last_request_time = time.time()

			try:
				responseDict = json.loads(response.content)
			except ValueError:
				rejectAlbums.append(album)
				continue
			allLinks = responseDict.get("linksByPlatform")
			deezerLinks = None
			if allLinks is not None:
				deezerLinks = allLinks.get("deezer")
			if deezerLinks is None:
				# add entry to some other list or log so I know what got missed
				rejectAlbums.append(album)
				continue
			else:
				# if deezer is available, set deezer URL and ID and add to an array
				albumURL = deezerLinks.get("url")
				if albumURL is not None:
					album.deezer_URL = albumURL
				else:
					rejectAlbums.append(album)
					continue

				albumRawID = deezerLinks.get("entityUniqueId")
				if albumRawID is not None:
					rawIDSplit = albumRawID.split("::",1)
					if len(rawIDSplit) == 2:
						album.deezer_ID = rawIDSplit[1]
						album.deezer_isTrack = rawIDSplit[0] == "DEEZER_SONG"
						successAlbums.append(album)
					else:
						rejectAlbums.append(album)
						continue
		print(f"Done converting. Success Rate: {int((len(successAlbums)/len(albums))*10000)/100}%")
		return successAlbums, rejectAlbums
	
	def convertAlbumsToTracks(albums: list[Album], deezerToken: str):
		deezer_endpoint_params = {
			'access_token': deezerToken
		}

		# rate limiting groundwork
		requests_made = 0
		last_request_time = None
		rate_limit = 50
		# timeframe in seconds
		rate_timeframe = 5

		# Construct API endpoint URL
		def get_api_url(forAlbum: Album):
			return f"https://api.deezer.com/album/{forAlbum.deezer_ID}/tracks"

		successTracks: list[Album] = []
		rejectAlbums: list[Album] = []

		for album in albums:
			# rate limit self while requesting API
			if requests_made >= rate_limit and last_request_time is not None:
				time_since_last_request = time.time() - last_request_time
				if time_since_last_request < rate_timeframe:
					time_to_wait = rate_timeframe - time_since_last_request
					print(f"[{datetime.datetime.now().time()}]: Sleeping...")
					time.sleep(time_to_wait)
					print(f"[{datetime.datetime.now().time()}]: Awoken!")
					requests_made = 0
					last_request_time = None

			if album.deezer_isTrack:
				successTracks.append(album)
			else:
				# if not a track, we need to get the tracks within the album
				#	with the Deezer API

				response = requests.get(get_api_url(forAlbum=album),params=deezer_endpoint_params)

				# update rate limiting variables
				requests_made += 1
				last_request_time = time.time()

				try:
					responseDict = json.loads(response.content)
				except ValueError:
					print("ahhhhhhh nooooo ahh man what no how could it do that")
					rejectAlbums.append(album)
					continue

				data = responseDict.get("data")

				if data is None:
					rejectAlbums.append(album)
					continue
				else:
					for track in data:
						tID = track.get("id")

						if tID is not None:
							processedTrack = Album.createTrack(trackData=track,albumData=album)
							successTracks.append(processedTrack)
						else:
							print(f"Assuming all tracks on this album are invalid, as no ID was found for one. Content of response is below... \n\n{response.content}\n\nEND OF RESPONSE FOR FAILED TRACK CONVERSION\n")
							rejectAlbums.append(album)

							# breaking here breaks the innermost loop only,
							# meaning we add this album as problematic (reject) and
							# move onto the next one instead. 
							# If one track is bad, we'll just assume the rest are bad as well
							break
		
		return successTracks, rejectAlbums
