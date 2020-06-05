import os
import pymysql
import requests
import json
from datetime import datetime

response = requests.get(
    "http://api.sportradar.us/nba/trial/v7/en/games/2019/REG/schedule.json?api_key=qhjbwd99fwtzvpasey7ebj7t")
# Print the status code of the response.
data = json.loads(response.content.decode("utf-8"))
schedule = []
for i in data["games"]:
    schedule.append({"id": i["id"],
                     "home": i["home"]["id"],
                     "away": i["away"]["id"],
                     "scheduled": i["scheduled"]})

username = os.getenv('C9_USER')
connection = pymysql.connect(host='localhost',
                             user=username,
                             password='',
                             db='rtg')
try:
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:

        for i in schedule:
            id = i["id"]
            home = i["home"]
            away = i["away"]
            date = str.split(i["scheduled"], 'T')
            date_f = date[0]
            print (id,home,away,date_f)
            cursor.execute(
                f"INSERT INTO Games (`GameId`, `Home_Team_Id`, `Away_Team_Id`, `Scheduled`) Values ('{id}','{home}','{away}','{date_f}')")
    connection.commit()
finally:
    connection.close()
