import os
import pymongo
import requests
import json
if os.path.exists('env.py'):
    import env

api_key = os.environ.get('api_key')
api_link = "http://api.sportradar.us/nba/trial/v7/en/games/2019/REG/schedule.json?api_key=%s" % api_key
response = requests.get(api_link)

#data = json.loads(response.content.decode("utf-8"))
#schedule = []

MONGODB_URI = os.environ.get("MONGO_URI")
DBS_NAME = 'rtg'
COLLECTION_NAME = '19schedule'


def get_api(game_id):
    api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
    response = requests.get(api_link.format(game_id, api_key))
    data = json.loads(response.content.decode("utf-8"))
    game_data = []
    game_data.append({"game_id": data["id"],
                      "lead_changes": data["lead_changes"],
                      "home": {"score": data["home"]["points"],
                               "name": data["home"]["name"]},
                      "away": {"score": data["away"]["points"],
                               "name": data["away"]["name"]},
                      "raw_data": data
                      })
    print(game_data)


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        print("Mongo is connected!")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDb: %s") % e


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
    return games


# for doc in documents:
#   print(doc)
