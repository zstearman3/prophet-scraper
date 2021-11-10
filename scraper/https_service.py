import os
import requests
import psycopg2
import json
from datetime import datetime
from psycopg2 import Error
from bs4 import BeautifulSoup

class HTTPSService:
  BASE_URL = 'https://www.espn.com/mens-college-basketball'

  def __init__(self, database="db/prophet_dev"):
    self.connection = psycopg2.connect(user=os.getenv('PG_USER'),
                                       password=os.getenv('PG_PASSWORD'),
                                       host=os.getenv('PG_HOST'),
                                       port="5432",
                                       database=os.getenv('PG_DATABASE'))

  def schedule(self, date):
    date_string = datetime.strftime(date, "%Y%m%d")
    url = f'{HTTPSService.BASE_URL}/scoreboard/_/group/50/date/{date_string}?xhr=1'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    schedule_json = json.loads(soup.text)
    games = schedule_json['content']['sbData']['events']

    return games

  def box_score(self, espn_id):
    url = f'{HTTPSService.BASE_URL}/boxscore?gameId={espn_id}&xhr=1'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    game_json = json.loads(soup.text)
    header = game_json["gamepackageJSON"]["header"]
    box_score = game_json["gamepackageJSON"]["boxscore"]
    # plays = game_json["gamepackageJSON"]["plays"]

    return {"header": header, "box_score": box_score}

  def roster(self, team_id):
    roster = []
    generic_url = HTTPSService.BASE_URL + "/team/roster/_/id/"
    full_url = generic_url + str(team_id)
    page = requests.get(full_url)

    soup = BeautifulSoup(page.content, 'html.parser')
    players = soup.find(class_='Roster').find_all(class_="Table__TR")
    for player in players:
      attributes = player.find_all("td")
      if len(attributes) > 0:
        record = {}
        record["espn_url"] = attributes[1].find("a").get("href")
        record["name"] = attributes[1].find("a").get_text()
        number_html = attributes[1].find("span")
        record["number"] = int(number_html.get_text()) if number_html else 0
        record["position"] = attributes[2].get_text()
        record["height"] = attributes[3].get_text()
        record["weight"] = attributes[4].get_text()
        record["class"] = attributes[5].get_text()
        record["birthplace"] = attributes[6].get_text()
        roster.append(record)
    return roster