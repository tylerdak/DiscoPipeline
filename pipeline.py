import threading

from AMController import AMController
from AMTokenGeneration import AMToken


class Pipeline:
	amToken = None
	deezerToken = None
	
	def setTimer(self):
		self.timer = threading.Timer(10.0, self.repeated)
		self.timer.start()

	def __init__(self, amToken=None, deezerToken=None) -> None:

		if [amToken,deezerToken] != [None,None]:
			print("new object token update")
			self.updateTokens(amToken,deezerToken)

		print("new object repeated action")
		self.repeated()

		# reenable in prod
		# self.setTimer()

	def updateTokens(self,amus,deez):
		print("about to update tokens")
		self.amToken = amus
		self.deezerToken = deez
		print("tokens are updated")

	def repeated(self):
		if AMToken.last is None:
			print("TOKEN SHOULD BE GENERATED BY THIS POINT")
		AMController.getAllLibrarySongs(self.amToken,AMToken.last)
		
		# reenable with reasonable time interval
		# after app is tested
		# self.setTimer()

	def getAppleMusicLibraryList():



		pass

	def getDiff():
		pass

	def addDiffToDeezer():
		pass

	def useDeemixToRetrieveOnServer():
		pass