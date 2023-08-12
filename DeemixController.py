from deemix import *
from deezer import Deezer

from deemix.settings import load as loadSettings
from deemix.downloader import Downloader
from deemix.utils import formatListener
import deemix

class LogListener:
    @classmethod
    def send(cls, key, value=None):
        logString = formatListener(key, value)
        if logString: print(logString)


class DeemixController:
	def downloadPlaylist(playlistID: str|int,arl: str):
		try:
			dz = Deezer()
			listen = LogListener()
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
				Downloader(dz, obj, settings, listen).start()
			return True
		except:
			return False