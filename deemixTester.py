from tqdm import tqdm
from DeemixController import DeemixController as dc
from Song import Album

from secretsHandler import deezerARL

# USER ARL
arl = deezerARL

# once we have the albums, we need to loop over them, and then add each of them to a deezer playlist... maybe favorites would be easier?
playlistAdditionOutput = {"code":200, "playlists":[11274921824,11274921804,11274921764,11274921744,11274921724,11274921684]}

paoCode = playlistAdditionOutput.get("code")

logfolder = "test/logs"

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

rejectAlbums = []
errorFlags = []
if rejectAlbums is not None and len(rejectAlbums) > 0:
	errorFlags.append("failedAlbumsConvert")
if rejectTracks is not None and len(rejectTracks) > 0:
	errorFlags.append("failedTracks")

failedDownloads = []
for playlist in tqdm(playlists):
	if not dc.downloadPlaylist(playlist,arl):
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
# dbstuff.insertSyncLog(errorFlags)