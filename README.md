## DiscoPipeline
### Some real niche shit 

---

DiscoPipeline is a web server designed to migrate a user's Apple Music library to local storage via Deezer and Deemix. This project is intended for educational purposes, only. Documentation is unfinished, for now.

![DiscoPipeline Image](image.webp)


### Usage
Feel free to use either as a docker container (recommended) or just run it with Python directly. Dockerfile has been included for you. I'd just recommend setting up a volume for your music folder, and probably your databases as well (mongo).

The secret file needs to include the following properties:
```
secret_key_filename = 'YOUR_KEY_FILE.p8'

f = open(secret_key_filename, 'r')

secret_key = f.read()
key_id = 'YOUR_APPLE_KEY_ID'
team_id = 'YOUR_APPLE_TEAM_ID'

deezerAppID = 'YOUR_DEEZER_APP_ID'
deezerKey = 'YOUR_DEEZER_API_KEY'

deezerARL = "YOUR_ARL"
```

Note that the ARL requirement will probably be phased out in favor of a webUI solution. If I really have time and motivation to work on this, the rest of the requirements will be phased out for that solution as well, but don't look forward to that.