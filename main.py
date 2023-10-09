# DiscoPipeline
# A musical pipeline from Apple Music, to Deezer, to deemix, to my local music folder :)

# import AMHandler
from types import NoneType

import requests
from DeemixController import DeemixController
from secret import secret_key
from flask import Flask, flash, redirect, render_template, request
import json
from AMTokenGeneration import *
from pipeline import Pipeline
import random
import string

from dbstuff import getUserTokens, setUserTokens, settingConstructor, setSettings, getSettings

def randomString(length: int = 32):
	return ''.join(random.choices(string.ascii_letters + string.digits,k=length))

# am = AMHandler.AppleMusic(secret_key,key_id,team_id)
# results = am.searchLibrary('inferno rich edwards', types=['songs'],limit=5)

# for item in results['results']['songs']['data']:
#     print(item['attributes'])

app = Flask(__name__)
app.secret_key = randomString()

# prepare a dev token for the auto-initiated Pipeline to use.
# this gets updated any time a user visits the endpoint,
# but could probably just update every time self.repeated runs for simplicity 

# Pipeline just uses the last AMToken anyway, so as it stands a user has to visit the site
# once every 6 months at least for it to not shit itself
AMToken.generate()

initAMToken, initDToken = getUserTokens()
pipelineInstance: Pipeline|NoneType = Pipeline(initAMToken,initDToken)


@app.after_request
def add_header(response):
    response.headers['Referrer-Policy'] = 'origin-when-cross-origin'


    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'

    return response

@app.route('/')
def index():
    aToken,dToken = getUserTokens()
    # print("getUserTokens: ", aToken,dToken)
    aToken=aToken if aToken != None else ""
    dToken=dToken if dToken != None else ""

    settings = getSettings(list(Pipeline.settingsKeys.keys()))
    settings = sorted(list(settings.items()),key=lambda x:x[0])
    
    sendSettings = []

    for setting in settings:
        if setting[1] is None or setting[1]["value"] is None:
            sendSettings.append({
                "key":setting[0],
                "name":Pipeline.settingsKeys[setting[0]],
                "value":""
            })
        else:
            sendSettings.append(setting[1])
    
    sendSettings.append(settingConstructor(
        key="downloadLocation",
        value=DeemixController.readSaveLocation(),
        name="Download Folder Location"
    ))

    return render_template('index.html', dev_token=AMToken.last if AMToken.last is not None else "", 
        amToken=aToken,
        deezerToken=dToken,
        settings=sendSettings
    )

@app.route('/submit-data', methods=['POST'])
def submit_data():
    tokens = json.loads(request.get_data())

    global pipelineInstance
    # print("about to set tokens: ", tokens['amToken'], tokens['deezerToken'])
    setUserTokens(tokens['amToken'],tokens['deezerToken'])

    if pipelineInstance is None:
        pipelineInstance = Pipeline(tokens['amToken'], tokens['deezerToken'])    
    else:
        pipelineInstance.updateTokens(tokens['amToken'], tokens['deezerToken'])
    return redirect('/')

@app.route('/deeznuts', methods=['GET'])
def deezerRedirect():
    redirectURI = request.host_url+"incomingDeezerCode"
    return redirect(f"https://connect.deezer.com/oauth/auth.php?app_id={secret.deezerAppID}&redirect_uri={redirectURI}&perms=basic_access,offline_access,manage_library,delete_library")

@app.route('/incomingDeezerCode')
def incomingDeezerCode():
    response = requests.get(f"https://connect.deezer.com/oauth/access_token.php?app_id={secret.deezerAppID()}&secret={secret.deezerKey()}&code={request.args.get('code')}")
    if response.status_code == 200:
        try:
            dToken = str(response.content).split('=',1)[1].split('&')[0]
            # set only the dToken, leaving the AMToken the same as before
            print("setting dToken: ",dToken)
            setUserTokens(getUserTokens()[0],dToken)
            if pipelineInstance is not None:
                pipelineInstance.deezerToken = dToken
        except IndexError:
            # print(response.content)
            pass
    # else:
    # print(response.content)
    return redirect('/')

@app.route('/deezerLogOut')
def deezerLogOut():
    setUserTokens(getUserTokens()[0],None)
    if pipelineInstance is not None:
        pipelineInstance.deezerToken = None
    return redirect("/")

@app.route('/amLogOut')
def amLogOut():
    setUserTokens(None,getUserTokens()[1])
    if pipelineInstance is not None:
        pipelineInstance.amToken = None
    return redirect("/")

@app.route('/settings',methods=["POST"])
def submitSettings():
    # if None in getUserTokens():
    #     flash("Both Apple Music and Deezer must be connected to adjust settings.", category="error")
    settings = []
    for item in Pipeline.settingsKeys.items():
        key = item[0]
        setting = settingConstructor(
            key=key,
            value=request.form.get(key),
            name=item[1]
        )
        settings.append(setting)
    
    downloadLocation = request.form.get("downloadLocation")
    if downloadLocation and type(downloadLocation) == str:
        DeemixController.editSaveLocation(downloadLocation)
    else:
        DeemixController.editSaveLocation("")

    setSettings(settings)

    # prepare AMToken in case it wasn't prepared
    AMToken.generate()

    return redirect("/")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)