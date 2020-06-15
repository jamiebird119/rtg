import os
import json
import pymongo
from flask import Flask, render_template, json, request
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
    return render_template("index.html")


@app.route('/<date>', methods=["GET", "POST"])
# Search schedule for games on date and return 2 teams and game id
def search_schedule():
    date = request.form["date"]
    conn = mongo_connect(MONGODB_URI)
    coll = conn[DBS_NAME][COLLECTION_NAME]
    search = {"date": date}
    documents = coll.find(search)
    games = []
    for doc in documents:
        games.append({"home": doc["home_team"],
                      "away": doc["away_team"],
                      "id": doc["id"]})
    return render_template("date.html",
                           date=date,
                           schedule_data=games
                           )


@app.route('/{id}')
def search_update(id):
    def search_games(id):
        conn = mongo_connect(MONGODB_GAME_URI)
        coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
        search = {"id": id}
        documents = coll.find(search)
        games = []
        games.append(documents)
        # if statement to check if data exists in database - if yes return - if no search api for data and save to database then return
        if games == []:
            game_data = get_api(id)
            save_game_data(game_data)
            rating = {game_data.lead_changes}
            return render_template("rating.html",
                                   rating=rating)
        else:
            return render_template("rating.html",
                                   rating=games.lead_changes)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)


def get_api(id):
    api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
    response = requests.get(api_link.format(id, api_key)).json()
    data = response
    game_data = []
    game_data.append({"game_id": data["id"],
                      "lead_changes": data["lead_changes"],
                      "home": {"score": data["home"]["points"],
                               "name": data["home"]["name"]},
                      "away": {"score": data["away"]["points"],
                               "name": data["away"]["name"]},
                      "raw_data": data
                      })
    return(game_data)


def save_game_data(data):
    conn = mongo_connect(MONGODB_GAME_URI)
    coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
    games = [data]
    coll.insert({"id": data["id"]},
                {"lead_changes": data["lead_changes"]},
                {"home": {
                 {"score": data["home"]["score"]},
                 {"name": data["home"]["name"]}}})
    coll.update({"id": data["id"]},
                {"$set": {"raw_data": data["raw_data"]}},
                multi=True)
    return data
