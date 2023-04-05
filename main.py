# DiscoPipeline
# A musical pipeline from Apple Music, to Deezer, to deemix, to my local music folder :)

# import AMHandler
from types import NoneType
from secret import secret_key, key_id, team_id
from flask import Flask, redirect, render_template, request
import json
from AMTokenGeneration import *
from pipeline import Pipeline

# am = AMHandler.AppleMusic(secret_key,key_id,team_id)
# results = am.searchLibrary('inferno rich edwards', types=['songs'],limit=5)

# for item in results['results']['songs']['data']:
#     print(item['attributes'])

app = Flask(__name__)

pipelineInstance: Pipeline|NoneType = None

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
    return render_template('index.html', dev_token=AMToken.generate())

@app.route('/submit-data', methods=['POST'])
def submit_data():
    tokens = json.loads(request.get_data())

    global pipelineInstance

    if pipelineInstance is None:
        pipelineInstance = Pipeline(tokens['amToken'], tokens['deezerToken'])    
    else:
        pipelineInstance.updateTokens(tokens['amToken'], tokens['deezerToken'])
    return redirect('/')

if __name__ == '__main__':
    app.run()