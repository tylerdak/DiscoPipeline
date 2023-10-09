import datetime

from tqdm import tqdm
import dbstuff
import json
import os
import threading

from AMController import AMController
from AMTokenGeneration import AMToken
from ConversionController import ConversionController
from DeemixController import DeemixController
from DeezerController import DeezerController
from Song import Album
import secretsHandler


class Pipeline:
	amToken = None
	deezerToken = None
	
	def setTimer(self):
		self.timer = threading.Timer(600.0, self.repeated)
		self.timer.start()

	def __init__(self, amToken=None, deezerToken=None) -> None:

		if [amToken,deezerToken] != [None,None]:
			# print("new object token update")
			self.updateTokens(amToken,deezerToken)

		# print("new object repeated action")
		self.repeated()

		# reenable in prod
		# self.setTimer()

	def updateTokens(self,amus,deez):
		# print("about to update tokens")
		self.amToken = amus
		self.deezerToken = deez
		# print("tokens are updated")

	settingsKeys = {"apple_dev_key_id":"Apple Developer Key","apple_dev_team_id":"Apple Developer Team ID","deezer_dev_key":"Deezer Developer Key","deezerAppID":"Deezer App ID","deezerARL":"Deezer ARL"}
	def areSettingsMissing():
		results = dbstuff.getSettings(list(Pipeline.settingsKeys.keys()))

		for result in results.items():
			if result[1] == None:
				return True
			if result[1].get("value") in [None,""]:
				print("Could not find value for ",result.get("key"))
				return True
		return False

	def repeated(self):
		print("Cycle disabled...")
		return

		print("\n\n\nBeginning cycle...")

		if Pipeline.areSettingsMissing():
			print("Could not find appropriate settings in database.")
			print("User must fill out settings form and submit.")
		elif AMToken.last is None:
			print("Apple Music devtoken has not been stored yet... returning for safety")
		elif self.amToken is None or self.deezerToken is None:
			print("At least one of two crucial music service tokens is set to none (am, deez): ", self.amToken, self.deezerToken)
			print("Returning for safety...")
		else:
			# continue with normal 

			dzController = DeezerController(deezerToken=self.deezerToken)
			# clean playlist list first
			dzController.deleteExcessPlaylists(500)

			# at the end we'll output this list somewhere,
			# but this is the list of albums that couldn't get
			# added to the playlist for whatever reason
			rejectAlbums: list[Album] = []


			# file compatible datestamp
			datestamp = datetime.datetime.now().isoformat().replace(":","").replace(".","-")
			# create logs folder
			logfolder = f"logs/log_{datestamp}"
			os.mkdir(logfolder)

			albums = self.getAppleMusicLibraryList(logfolder)
			if len(albums) == 0:
				print("No albums found, skipping conversion for this round.")
				# dbstuff.insertSyncLog(["none"])
				self.setTimer()
				return


			success, noMatch = self.addDeezerLinks(albums=albums)
			rejectAlbums += noMatch

			# albums can't be added to a playlist, so we first need to
			# 	convert any albums in this list to tracks instead.
			# we can do this by using the deezer_isTrack property, and
			#	converting any of the objects with that property false.
			# then, we can just add all of the track objects 
			# 							(which are really albums marked as tracks)
			# 	to an array that we will then pass to the playlist API
			successTracks, albumConversionFail = self.convertAlbumsToTracks(albums=success)
			rejectAlbums += albumConversionFail

			# output failed albums to log file
			if not Album.exportCSV(rejectAlbums,logfolder,"failedAlbumConverts"):
				print("failed to export failedAlbums log")

			print(f"Just converted albums to tracks, new count is {len(successTracks)} tracks.")
			if len(rejectAlbums) > 0:
				print(f"Also relevant: We've had {len(rejectAlbums)} albums fail to convert. F.")
				print(f"List of albums:")
				for album in rejectAlbums:
					print(f"{album.artistName} - {album.title}")

			# USER ARL
			arl = secretsHandler.deezerARL()

			# once we have the albums, we need to loop over them, and then add each of them to a deezer playlist... maybe favorites would be easier?
			playlistAdditionOutput = dzController.addTracksToPlaylist(tracklist=successTracks)

			paoCode = playlistAdditionOutput.get("code")

			rejectTracks = []
			playlists = []

			if paoCode == 400:
				print("All tracks rejected, invalid playlist ID likely")
			elif paoCode == 300:
				rejectTracks = playlistAdditionOutput.get("tracks")
				if rejectTracks is not None:
					Album.exportCSV(rejectTracks,logfolder,"failedTracks")
				newPlaylists = playlistAdditionOutput.get("playlists")
				if newPlaylists is not None:
					playlists = newPlaylists
			elif paoCode == 401:
				print("No token provided to Deezer playlist adder.")
			elif paoCode == 200:
				print("All's well I guess.")
				newPlaylists = playlistAdditionOutput.get("playlists")
				if newPlaylists is not None:
					playlists = newPlaylists
			else:
				print(f"Did not find any registered paoCode.\nplaylistAdditionOutput:\n{json.dumps(playlistAdditionOutput)}")

			errorFlags = []
			if rejectAlbums is not None and len(rejectAlbums) > 0:
				errorFlags.append("failedAlbumsConvert")
			if rejectTracks is not None and len(rejectTracks) > 0:
				errorFlags.append("failedTracks")

			failedDownloads = []
			for playlist in tqdm(playlists):
				if not DeemixController.downloadPlaylist(playlist,arl):
					tqdm.write("Failed to download: ", playlist)
					failedDownloads.append(playlist)


			fileLabel = "failedDownloads"
			for failedDownload in failedDownloads:
				with open(f"{logfolder}/{fileLabel}.csv","w") as f:
					f.write(failedDownload)
					f.close()
				with open(f"{logfolder}/{fileLabel}.log","w") as f:
					f.write(failedDownload)
					f.close()

			# save the date
			dbstuff.insertSyncLog(errorFlags)
		
		# DEFER
		# reenable with reasonable time interval
		# after app is tested
		self.setTimer()

	def getAppleMusicLibraryList(self,logfolder):
		return AMController.getAllLibrarySongs(self.amToken,AMToken.last,logfolder)

	def addDeezerLinks(self,albums):
		return ConversionController.addDeezerLinks(albums=albums)
	
	def convertAlbumsToTracks(self,albums: list[Album]):
		return ConversionController.convertAlbumsToTracks(albums=albums, deezerToken=self.deezerToken)


	def addDiffToDeezer(albums: list[Album]):
		for album in albums:
			album.am_storeURL
		pass

	def useDeemixToRetrieveOnServer():
		pass