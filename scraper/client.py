import os
import requests
import psycopg2
from psycopg2 import Error
from bs4 import BeautifulSoup

from scraper.https_service import HTTPSService

class Client:

  def __init__(self, database="db/prophet_dev"):
    self.connection = psycopg2.connect(user="ec2-user",
                                       password = os.getenv('PG_PASSWORD'),
                                       host="127.0.0.1",
                                       port="5432",
                                       database=database)

  def _get_espn_ids(self, team_id=None):
    try:
      cursor = self.connection.cursor()
      if team_id:
        cursor.execute(f"SELECT id, espn_id, school FROM teams WHERE id={team_id}")
      else:
        cursor.execute("SELECT id, espn_id, school FROM teams")
      espn_ids = cursor.fetchall()
    except(Exception, Error) as error:
      print("Error while connecting to PostgreSQL", error)
    finally:
      if (self.connection):
        cursor.close()
        return espn_ids

  def schedule(self):
    service = HTTPSService()
    games = service.schedule()
    return games

  def hierarchy(self):
    service = HTTPSService()

  def rosters(self):
    rosters = {}
    service = HTTPSService()
    espn_ids = self._get_espn_ids()
    for espn_id in espn_ids:
      roster = service.roster(team_id=espn_id[1])
      rosters[espn_id[0]] = roster
    return rosters