import dbstuff

from secret import secret_key_filename

f = open(secret_key_filename, 'r')

secret_key = f.read()

def key_id(): 
	try: 
		return dbstuff.getSettings("apple_dev_key_id").get("value") 
	except AttributeError: 
		print(dbstuff.getSettings("apple_dev_key_id"))
		return None 
def team_id(): 
	try: 
		return dbstuff.getSettings("apple_dev_team_id").get("value") 
	except AttributeError: 
		return None 

def deezer_dev_key():  
	try: 
		return dbstuff.getSettings("deezer_dev_key").get("value") 
	except AttributeError: 
		return None
	
def deezerAppID():  
	try: 
		return dbstuff.getSettings("deezerAppID").get("value") 
	except AttributeError: 
		return None 

def deezerARL():  
	try: 
		return dbstuff.getSettings("deezerARL").get("value") 
	except AttributeError: 
		return None 