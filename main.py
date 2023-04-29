# DiscoPipeline
# A musical pipeline from Apple Music, to Deezer, to deemix, to my local music folder :)

# import AMHandler
from types import NoneType

import requests
from secret import secret_key, key_id, team_id
from flask import Flask, redirect, render_template, request
import json
from AMTokenGeneration import *
from pipeline import Pipeline

from dbstuff import getUserTokens, setUserTokens

# am = AMHandler.AppleMusic(secret_key,key_id,team_id)
# results = am.searchLibrary('inferno rich edwards', types=['songs'],limit=5)

# for item in results['results']['songs']['data']:
#     print(item['attributes'])

app = Flask(__name__)

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

    return render_template('index.html', dev_token=AMToken.generate(), amToken=aToken,deezerToken=dToken)

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
    return redirect(f"https://connect.deezer.com/oauth/auth.php?app_id={secret.deezerAppID}&redirect_uri={redirectURI}&perms=basic_access,offline_access,manage_library")

@app.route('/incomingDeezerCode')
def incomingDeezerCode():
    response = requests.get(f"https://connect.deezer.com/oauth/access_token.php?app_id={secret.deezerAppID}&secret={secret.deezerKey}&code={request.args.get('code')}")
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)