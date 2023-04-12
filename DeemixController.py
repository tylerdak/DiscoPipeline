from deemix import *
from deezer import Deezer

from deemix.settings import load as loadSettings
from deemix.downloader import Downloader
import deemix

class DeemixController:
	def downloadPlaylist(playlistID: str|int,arl: str):
		try:
			dz = Deezer()
			dz.login_via_arl(arl=arl)

			settings = loadSettings('config/deemix')

			playlistURL = f"https://www.deezer.com/playlist/{playlistID}"

			downloadObjects = []
			dlObj = deemix.generateDownloadObject(dz,link=playlistURL,bitrate=settings.get("maxBitrate"))
			if isinstance(dlObj, list):
				downloadObjects += dlObj
			else:
				downloadObjects.append(dlObj)

			for obj in downloadObjects:
				Downloader(dz, obj, settings).start()
			return True
		except:
			return False