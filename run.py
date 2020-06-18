import os
import json
import pymongo
from flask import Flask, render_template, json, request, redirect
import requests
if os.path.exists('env.py'):
    import env


app = Flask(__name__)
api_key = os.environ.get('api_key')

MONGODB_URI = os.environ.get("MONGO_URI")
MONGODB_GAME_URI = os.environ.get("MONGO_GAME_URI")
DBS_NAME = 'rtg'
COLLECTION_NAME = '19schedule'
GAME_COLLECTION_NAME = 'game_data'


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        print("Mongo is connected!")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDb: %s") % e


@app.route('/')
def index():
    return render_template("base.html")


@app.route('/search/<date>', methods=["GET", "POST"])
# Search schedule for games on date and return 2 teams and game id
def search_schedule(date):
    if request.method == 'POST':
        conn = mongo_connect(MONGODB_URI)
        coll = conn[DBS_NAME][COLLECTION_NAME]
        search = {"date": date}
        documents = coll.find(search)
        games = []
        for doc in documents:
            games.append({"home": doc["home_team"],
                          "away": doc["away_team"],
                          "id": doc["id"]})
        return json.dumps(games)
    else:
        not_available = "The data is not available"
        return not_available


@app.route('/search/<id>', methods=["GET", "POST"])
def search_games(id):
    if request.method == 'POST':
        conn = mongo_connect(MONGODB_GAME_URI)
        coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
        search = {"game_id": id}
        documents = coll.find_one(search)
        games = []
        games.append(documents)
        # if statement to check if data exists in database - if yes return - if no search api for data and save to database then return
        if documents != []:
            return json.dumps(games)
        else:
            return "Nothing to see here"
            return json.dumps(get_api(id))
    else:
        return "The data is not available"


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)


def get_api(id):
    print("getting")
    conn = mongo_connect(MONGODB_GAME_URI)
    coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
    api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
    response = requests.get(api_link.format(id, api_key)).json()
    data = response
    coll.insert({"game_id": data["id"]},
                {"lead_changes": data["lead_changes"]},
                {"home": {
                 {"score": data["home"]["score"]},
                 {"name": data["home"]["name"]}}})
    coll.update({"id": data["id"]},
                {"$set": {"raw_data": data["raw_data"]}},
                multi=True)
    return data
