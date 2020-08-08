import os
import json
import pymongo
from flask import Flask, render_template, json, request, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
if os.path.exists('env.py'):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
api_key = os.environ.get("api_key")


mongo = PyMongo(app)


# Home Page with datepicker and top ten games rated
@app.route('/')
def index():
    docs = mongo.db.rating.find(sort=[("rating", pymongo.DESCENDING)], limit=10)
    top_ten = []
    for i in docs:
        game = mongo.db.schedule.find({"id": i["id"]})
        for thing in game:
            url = "/static/assets/rating.png".replace(
                "rating", str(round(i["rating"])))
            date_string = thing["date"]
            date_obj = datetime.strptime(date_string, "%Y-%m-%d")
            date = date_obj.strftime("%d %b %Y")
            top_ten.append({"rating": url,
                            "date": date,
                            "home": thing["home_team"],
                            "away": thing["away_team"]})
    return render_template("index.html", topTen=top_ten)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/search_by_date/<date>', methods=["GET", "POST"])
# Search schedule for games on date and return 2 teams and game id
def search_schedule(date):
    search = {"date": date}
    documents = mongo.db.schedule.find(search)
    games = []
    for doc in documents:
        print(doc)
        games.append({"home": doc["home_team"],
                      "away": doc["away_team"],
                      "id": doc["id"]})
    datetimeobject = datetime.strptime(date, '%Y-%m-%d')
    newformat = datetimeobject.strftime('%a %d %b %Y')
    return render_template("date.html", date=newformat, data=games)


# Search database for game data. If not found retrieve from API and save to database
@app.route('/search_by_id/<id>', methods=["GET", "POST"])
def search_games(id):
    if request.method == 'POST':
        search = {"game_id": id}
        documents = mongo.db.game_data.find_one(search)
        if documents:
            rating = ((0.015 * (documents["home"]["score"] + documents["away"]["score"])) - (0.01 * abs(
                documents["home"]["score"] - documents["away"]["score"])) + (0.06 * documents["lead_changes"]))
            return json.dumps([{"rating": rating}])
        else:
            api_link = "https://api.sportradar.us/nba/trial/v7/en/games/{}/boxscore.json?api_key={}"
            response = requests.get(api_link.format(id, api_key)).json()
            data = []
            if response["status"] == "closed":
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
                mongo.db.game_data.insert(data)
                mongo.db.rating.insert_one({"rating": rating, "id": id})

                return json.dumps([{"rating": rating}])
            else:
                return json.dumps([{"rating": "Not Available/Not played"}])
    else:
        return "The data is not available"


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
