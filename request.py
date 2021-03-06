import os
import pymongo
import requests
import json
if os.path.exists('env.py'):
    import env

api_key = os.environ.get('api_key')
api_link = "http://api.sportradar.us/nba/trial/v7/en/games/2019/REG/schedule.json?api_key=%s" % api_key

# data = json.loads(response.content.decode("utf-8"))
# schedule = []

MONGODB_URI = os.environ.get("MONGO_URI")
MONGODB_GAME_URI = os.environ.get("MONGO_GAME_URI")
MONGO_RATING_URI = os.environ.get("MONGO_RATING_URI")
DBS_NAME = 'rtg'
COLLECTION_NAME = 'schedule'
GAME_COLLECTION_NAME = 'game_data'
RATING_COLLECTION = 'rating'


def get_api(game_id):
    api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
    response = requests.get(api_link.format(game_id, api_key)).json()
    data = response
    game_data = {}
    game_data.append({"game_id": data["id"],
                      "lead_changes": data["lead_changes"],
                      "home": {"score": data["home"]["points"],
                               "name": data["home"]["name"]},
                      "away": {"score": data["away"]["points"],
                               "name": data["away"]["name"]},
                      "raw_data": data
                      })
    return(game_data)


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        print("Mongo is connected!")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDb: %s") % e


# Get schedule
def get_schedule():
    link = "http://api.sportradar.us/nba/trial/v7/en/games/2019/REG/schedule.json?api_key=qhjbwd99fwtzvpasey7ebj7t"
    conn = mongo_connect(MONGODB_URI)
    coll = conn[DBS_NAME][COLLECTION_NAME]
    response = requests.get(link).json()
    schedule = response
    for doc in schedule["games"]:
        game = {"id": doc["id"],
                "home_team": doc["home"]["name"],
                "home_short": doc["home"]["alias"],
                "away_team": doc["away"]["name"],
                "away_short": doc["away"]["alias"],
                "date": doc["scheduled"].split("T")[0],
                "time": doc["scheduled"].split("T")[1]}
        coll.insert_one(game)


get_schedule()


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
    return games


# Search Database for game from id and return game data
def search_games(id):

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
        print(search_data)
        return json.dumps(search_data)
    else:
        api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
        response = requests.get(api_link.format(id, api_key)).json()
        data = []
        print(response)
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
        rating = ((0.015 * (response["home"]["points"] + response["away"]["points"])) - (0.01 * abs(
            response["home"]["points"] - response["away"]["points"])) + (0.06 * response["lead_changes"]))
        coll.insert(data)
        col2.insert_one({"rating": rating, "id": id})

        from_saved = {"home": response["home"]["points"],
                      "away": response["away"]["points"],
                      "lead_changes": response["lead_changes"]}
        return json.dumps(from_saved)


# Search for schedule and save games
def get_schedule(api_key, api_link):
    response = requests.get(api_link.format(api_key)).json()
    data = response
    # schedule = []
    conn = mongo_connect(MONGODB_URI)
    coll = conn[DBS_NAME][COLLECTION_NAME]
    for i in data["games"]:
        date = i["scheduled"].split("T")
        coll.update_one({"id": i["id"]}, {'$set': {'date': date[0]}})
        coll.update_one({"id": i["id"]}, {'$set': {'time': date[1]}})


def delete_objects():
    conn = mongo_connect(MONGODB_GAME_URI)
    coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
    coll.delete_many()


def get_ids():
    conn = mongo_connect(MONGODB_GAME_URI)
    coll = conn[DBS_NAME][GAME_COLLECTION_NAME]
    documents = coll.find()
    ratings = []
    for i in documents:
        rating = ((0.015 * (i["home"]["score"] + i["away"]["score"])) - (0.1 * abs(
            i["home"]["score"] - i["away"]["score"])) + (0.06 * i["lead_changes"]))
        id = i["game_id"]
        ratings.append({"id": id, "rating": rating})
    con2 = mongo_connect(MONGO_RATING_URI)
    col2 = con2[DBS_NAME][RATING_COLLECTION]
    for i in ratings:
        col2.update_one({"id": i["id"]}, {"$set": {"rating": i["rating"]}})
