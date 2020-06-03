import os
import pymysql
import requests
import json
import datetime

response = requests.get(
    "http://api.sportradar.us/nba/trial/v7/en/games/2019/REG/schedule.json?api_key=qhjbwd99fwtzvpasey7ebj7t")
# Print the status code of the response.
data = json.loads(response.content.decode("utf-8"))
schedule = []
for i in data["games"]:
    schedule.append({i["id"],
                    i["home"]["id"],
                    i["away"]["id"],
                    i["scheduled"]})

username = os.getenv('C9_USER')
connection = pymysql.connect(host='localhost',
                             user=username,
                             password='',
                             db='rtg')
try:
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:

        for i in schedule:
            cursor.execute("INSERT INTO Games(GameId, Home_Team_Id, Away_Team_Id, Scheduled) Values ({})", i)
    connection.commit()
finally:
    connection.close()
