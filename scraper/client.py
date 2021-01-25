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

  def get_rosters(self):
    rosters = {}
    service = HTTPSService()
    espn_ids = self._get_espn_ids()
    for espn_id in espn_ids:
      roster = service.roster(team_id=espn_id[1])
      rosters[espn_id[0]] = roster
    return rosters

  def update_roster(self, team_id, roster):
    keys, roster = self.convert_roster_to_tuples(roster, team_id)
    print(keys)
    print(roster[0])
    try:
      query = """
        INSERT INTO players {0}
        VALUES %s;
      """.format(keys)
      cursor = self.connection.cursor()
      cursor.execute(query, (roster[0], ))
    except(Exception, Error) as error:
      print("Error while connecting to PostgreSQL", error)
    self.connection.commit()

  def _get_positions_and_klasses(self):
    try:
      cursor = self.connection.cursor()
      cursor.execute("SELECT abbreviation, id FROM positions")
      positions = dict(cursor.fetchall())
      cursor.execute("SELECT abbreviation, id FROM klasses")
      klasses = dict(cursor.fetchall())
      return(positions, klasses)
    except(Exception, Error) as error:
      print("Error while connecting to PostgreSQL", error)

  def convert_roster_to_tuples(self, roster, team_id):
    positions, klasses = self._get_positions_and_klasses()
    keys = ("first_name",
           "last_name",
           "number",
           "position",
           "class",
           "height",
           "weight",
           "birthplace",
           "espn_id",
           "espn_url",)
    keys_string = "("
    for key in keys:
      keys_string += f"{key}, "
    keys_string += "team_id)"
    keys_string = keys_string.replace("number", "jersey_number")
    keys_string = keys_string.replace("position", "position_id")
    keys_string = keys_string.replace("class", "klass_id")
    roster_tuples = []
    for player in roster:
      player_list = []
      for key in keys:
        if key == "position":
          try:
            position_id = positions[player[key]]
          except KeyError:
            position_id = None
          player_list.append(position_id)
        elif key == "class":
          try:
            klass_id = klasses[player[key]]
          except KeyError:
            klass_id = None
          player_list.append(klass_id)
        else:
          player_list.append(player[key])
      player_list.append(team_id)
      player_tuple = tuple(player_list)
      roster_tuples.append(player_tuple)
    return keys_string, roster_tuples