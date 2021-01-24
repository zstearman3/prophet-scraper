import os
import requests
import psycopg2
from psycopg2 import Error
from bs4 import BeautifulSoup

class HTTPSService:
  BASE_URL = 'https://www.espn.com/mens-college-basketball'

  def __init__(self, database="db/prophet_dev"):
    self.connection = psycopg2.connect(user="ec2-user",
                                       password = os.getenv('PG_PASSWORD'),
                                       host="127.0.0.1",
                                       port="5432",
                                       database=database)

  def schedule(self):
    url = f'{HTTPSService.BASE_URL}/scoreboard'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    games = soup.find_all('div', class_='scoreboards')

    print(games)
    return games

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