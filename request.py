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


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        print("Mongo is connected!")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDb: %s") % e


conn = mongo_connect(MONGODB_URI)


coll = conn[DBS_NAME][COLLECTION_NAME]


documents = coll.find()


for doc in documents:
    print(doc)
