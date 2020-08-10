import os
import json
import pymongo
from flask import Flask, render_template, json, request, redirect
import requests
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
    docs = mongo.db.rating.find(
        sort=[("rating", pymongo.DESCENDING)], limit=5)
    top_ten = []
    for i in docs:
        game = mongo.db.schedule.find({"id": i["id"]})
        for thing in game:
            url = "/static/assets/rating.png".replace(
                "rating", str(round(i["rating"])))
            date_string = thing["date"]
            date_obj = datetime.strptime(date_string, "%Y-%m-%d")
            date = date_obj.strftime("%b %d %Y")
            top_ten.append({"rating": url,
                            "date": date,
                            "home": thing["home_team"],
                            "away": thing["away_team"]})
    teams_home = mongo.db.teams.find(
        sort=[("home_average", pymongo.DESCENDING)], limit=3)
    top_home = []
    for doc in teams_home:
        print(doc)
        url = "/static/assets/rating.png".replace(
            "rating", str(round(doc["home_average"])))
        img = 'static/assets/logos/name.gif'.replace('name', doc["team_short"])
        top_home.append({"average_rating": url,
                         "img": img,
                         "team_name": doc["team_name"]})
    teams_away = mongo.db.teams.find(
        sort=[("away_average", pymongo.DESCENDING)], limit=3)
    top_away = []
    for doc in teams_away:
        url = "/static/assets/rating.png".replace(
            "rating", str(round(doc["away_average"])))
        img = 'static/assets/logos/name.gif'.replace('name', doc["team_short"])
        top_away.append({"average_rating": url,
                         "img": img,
                         "team_name": doc["team_name"]})
    return render_template("index.html",
                           topTen=top_ten,
                           topHome=top_home,
                           topAway=top_away)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/search_by_date/', methods=["POST"])
# Search schedule for games on date and return 2 teams and game id
def search_schedule():
    date = request.form.get("date")
    search = {"date": date}
    documents = mongo.db.schedule.find(search)
    games = []
    for doc in documents:
        games.append({"home": doc["home_team"],
                      "away": doc["away_team"],
                      "id": doc["id"]})
    datetimeobject = datetime.strptime(date, '%Y-%m-%d')
    newformat = datetimeobject.strftime('%a %b %d %Y')
    return render_template("date.html",
                           date_old=date,
                           date=newformat, data=games)


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


@app.route('/teams')
def teams():
    return render_template('teams.html')


@app.route('/search_teams', methods=["POST"])
def search_teams():
    team_name = request.form.get("team")
    team = request.form.get("team").split(" ")
    home = mongo.db.game_data.find({'home.name': team[(len(team)-1)]})
    away = mongo.db.game_data.find({'away.name': team[(len(team)-1)]})
    data_home = []
    home_ratings = []
    for item in home:
        home_ratings.append(mongo.db.rating.find({"id": item["game_id"]}))
    for i in home_ratings:
        for u in i:
            data_home.append(u["rating"])
    away_ratings = []
    data_away = []
    for item in away:
        away_ratings.append(mongo.db.rating.find({"id": item["game_id"]}))
    for i in away_ratings:
        for u in i:
            data_away.append(u["rating"])
    data = {"team_name": team_name,
            "team_short": team[(len(team)-1)],
            "home_ratings": data_home,
            "away_ratings": data_away}
    if len(data_home) > 0:
        home_average = sum(data_home)/len(data_home)
    else:
        home_average = 0

    if len(data_away) > 0:
        away_average = sum(data_away)/len(data_away)
    else:
        away_average = 0
    database = {"team_name": team_name,
                "team_short": team[(len(team)-1)],
                "home_ratings": data_home,
                "away_ratings": data_away,
                "games_rated": len(data_home) + len(data_away),
                "home_average": home_average,
                "away_average": away_average}
    if mongo.db.teams.find_one({"team_name": team_name}):
        mongo.db.teams.find_one_and_update(
            {"team_name": database["team_name"]}, {"$set": database})
        return render_template("teams.html", team_data=data)
    else:
        mongo.db.teams.insert_one(database)
        return render_template("teams.html", team_data=data)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
