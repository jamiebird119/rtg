import os
import json
import pymongo
from flask import Flask, render_template, json, request, redirect
from datetime import datetime
import requests
if os.path.exists('env.py'):
    import env


app = Flask(__name__)
api_key = os.environ.get('api_key')

MONGODB_URI = os.environ.get("MONGO_URI")
MONGODB_GAME_URI = os.environ.get("MONGO_GAME_URI")
MONGO_RATING_URI = os.environ.get("MONGO_RATING_URI")
DBS_NAME = 'rtg'
COLLECTION_NAME = '19schedule'
GAME_COLLECTION_NAME = 'game_data'
RATING_COLLECTION = 'rating'


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


@app.route('/search_by_date/<date>', methods=["GET", "POST"])
# Search schedule for games on date and return 2 teams and game id
def search_schedule(date):
    conn = mongo_connect(MONGODB_URI)
    coll = conn[DBS_NAME][COLLECTION_NAME]
    search = {"date": date}
    documents = coll.find(search)
    games = []
    for doc in documents:
        games.append({"home": doc["home_team"],
                      "away": doc["away_team"],
                      "id": doc["id"]})
    datetimeobject = datetime.strptime(date, '%Y-%m-%d')
    newformat = datetimeobject.strftime('%d/%m/%Y')
    return render_template("date.html", date=newformat, data=games)


@app.route('/search_by_id/<id>', methods=["GET", "POST"])
def search_games(id):
    if request.method == 'POST':
        print("2")
        conn = mongo_connect(MONGODB_GAME_URI)
        coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
        con2 = mongo_connect(MONGO_RATING_URI)
        col2 = con2[DBS_NAME][RATING_COLLECTION]
        search = {"game_id": id}
        documents = coll.find_one(search)
        if documents:
            search_data = {"home": documents["home"]["score"],
                           "away": documents["away"]["score"],
                           "lead_changes": documents["lead_changes"]}
            return json.dumps(search_data)
        else:
            api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
            response = requests.get(api_link.format(id, api_key)).json()
            data = []
            data.append(
                ({"game_id": response["id"],
                  "lead_changes": response["lead_changes"],
                  "home": {"score": response["home"]["points"],
                           "name": response["home"]["name"]},
                  "away": {"score": response["away"]["points"],
                           "name": response["away"]["name"]},
                  "raw_data": response
                  })
            )
            rating = (0.015 * (response["home"]["points"] + response["away"]["points"]) + 0.01 * abs(response["home"]["points"] - response["away"]["points"]) + 0.06 * response["lead_changes"])
            coll.insert(data)
            col2.insert_one({"rating": rating, "id": id})

            from_saved = {"home": response["home"]["points"],
                          "away": response["away"]["points"],
                          "lead_changes": response["lead_changes"]}
            return json.dumps(from_saved)
    else:
        return "The data is not available"


@ app.route('/get/<id>', methods=["GET", "POST"])
def get_api(id):
    if request.method == "POST":
        conn = mongo_connect(MONGODB_GAME_URI)
        coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
        api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
        response = requests.get(api_link.format(id, api_key)).json()
        data = []
        data.update(
            ({"game_id": response["id"],
              "lead_changes": response["lead_changes"],
              "home": {"score": response["home"]["points"],
                       "name": response["home"]["name"]},
              "away": {"score": response["away"]["points"],
                       "name": response["away"]["name"]},
              "raw_data": response
              })
        )
        # coll.insert(data)
        return data
    else:
        return "The data is not available"


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
