from datetime import date
import datetime
from fallback import alt

class Album:
	amData: dict

	# useful properties from amData that might be wanted
	def attrs(self): 		return self.amData.get("attributes")
	def catalogData(self):
		try: 	
			return self.amData.get("relationships").get("catalog").get("data")[0]
		except IndexError:
			return None
	def catID(self): 		return self.catalogData().get("id")
	def catAttrs(self): 	return self.catalogData().get("attributes")

	dateAdded: datetime
	dateAddedString: str
	title: str
	artistName: str
	am_storeURL: str
	releaseDateStr: str
	releaseDate: datetime

	deezer_URL: str = None
	deezer_ID: str = None
	deezer_isTrack: bool = False
	
	def __init__(self, amData) -> None:
		# print(amData)
		self.amData = amData

		self.title = self.attrs().get("name")
		self.artistName = self.attrs().get("artistName")
		self.dateAddedString = self.attrs().get("dateAdded")
		self.dateAdded = datetime.datetime.fromisoformat(self.dateAddedString)
		self.am_storeURL = self.catAttrs().get("url")
		self.releaseDateStr = self.catAttrs().get("releaseDate")

		# some of the dates I've seen with a year below 2000 have 
		# failed the isoformat test, so in case that happens, we'll
		# just manually assign the release date property, because it's 
		# literally only used to plan for _upcoming_ albums anyway
		if int(self.releaseDateStr[:4]) < 2000:
			self.releaseDate = datetime.datetime.fromisoformat("1976-04-10")
		else:
			try:
				self.releaseDate = datetime.datetime.fromisoformat(self.releaseDateStr)
			# if that sketchy-ass check for the year doesn't work (i'm sure dates past 2000 could be problematic sometimes too)
			# this exception will definitely catch them.
			except ValueError:
				self.releaseDate = self.releaseDate = datetime.datetime.fromisoformat("2001-04-10") 
				print("The following date could not be converted from isoformat. If this is an upcoming date, this album will not be retrieved unless the user readds the whole album when it comes out: ", self.releaseDateStr)

	def export(self) -> dict:
		return 	{
					"title": self.title, 
					"artistName": self.artistName, 
					"dateAdded": self.dateAddedString,
					"appleMusicID": self.catID(),
					"deezerID": self.deezer_ID,
					"dateAdded": self.dateAddedString,
					"isTrack": self.deezer_isTrack
				}
	
	def exportCSVHeaders() -> str:
		# make sure these headers match the order of the properties below (in exportCSVListing)
		return "artistName,title,appleMusicID,deezerID,dateAdded,isTrack"
	def exportCSVListing(self) -> str:
		return f"{self.artistName},{self.title},{self.catID()},{self.deezer_ID},{self.dateAddedString},{self.deezer_isTrack}"
	def exportCSV(importList,log_folder,fileLabel=None):
		try:
			csvOutput = Album.exportCSVHeaders()
			for album in importList:
				csvOutput += "\n" + album.exportCSVListing()
			
			if fileLabel is None:
				fileLabel = "genericAlbumOutput"

			with open(f"{log_folder}/{fileLabel}.csv","w") as f:
				f.write(csvOutput)
				f.close()
			with open(f"{log_folder}/{fileLabel}.log","w") as f:
				f.write(csvOutput)
				f.close()

			return True
		except:
			return False
		
	def exportPersonalUploads(personalUploads, log_folder,fileLabel="personalUploads"):
		try:
			csvOutput = "artistName,title"
			for song in personalUploads:
				title = song.get("attributes").get("name")
				artistName = song.get("attributes").get("artistName")
				csvOutput += "\n" + f"{artistName},{title}"

			with open(f"{log_folder}/{fileLabel}.csv","w") as f:
				f.write(csvOutput)
				f.close()
			with open(f"{log_folder}/{fileLabel}.log","w") as f:
				f.write(csvOutput)
				f.close()

			return True
		except:
			return False
		
	def checkDataForRequirements(data):
		print(amData)
		self.amData = amData

		self.title = self.attrs().get("name")
		self.artistName = self.attrs().get("artistName")
		self.dateAddedString = self.attrs().get("dateAdded")
		self.dateAdded = datetime.datetime.fromisoformat(self.dateAddedString)
		self.am_storeURL = self.catAttrs().get("url")
		self.releaseDateStr = self.catAttrs().get("releaseDate")

	
	def exportList(importList):
		return list(
			map(lambda album: album.export(), importList)
		)
	
	def createTrack(trackData, albumData):
		thisAlbum = Album(amData=albumData.amData)
		thisAlbum.title = trackData.get("title")
		thisAlbum.artistName = trackData.get("artist").get("name")
		thisAlbum.deezer_ID = trackData.get("id")
		thisAlbum.deezer_isTrack = True
		thisAlbum.deezer_URL = trackData.get("link")
		thisAlbum.deezer_URL.replace('\\\\','')
		return thisAlbum
