from datetime import date
import datetime

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

	dateAdded: date
	dateAddedString: str
	title: str
	artistName: str
	am_catalogID: str
	am_storeURL: str
	
	def __init__(self, amData) -> None:
		self.amData = amData

		self.title = self.attrs().get("name")
		self.artistName = self.attrs().get("artistName")
		self.dateAddedString = self.attrs().get("dateAdded")
		self.dateAdded = datetime.datetime.fromisoformat(self.dateAddedString).date()
		self.am_storeURL = self.catAttrs().get("url")

