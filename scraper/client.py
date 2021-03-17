import os
import requests
import psycopg2
from psycopg2 import Error
from bs4 import BeautifulSoup

from scraper.https_service import HTTPSService
from scraper.processor import Processor

def replace_keys(my_string):
  my_string = my_string.replace("number", "jersey_number")
  my_string = my_string.replace("position", "position_id")
  my_string = my_string.replace("class", "klass_id")
  return my_string

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
    processor = Processor()
    games = service.schedule()
    espn_ids = []
    game_results = []

    for game in games:
      espn_id = processor.get_espn_id(game)
      espn_ids.append(espn_id)
    for espn_id in espn_ids:
      results = service.box_score(espn_id)
      game_results.append(results)
    return game_results

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
    keys, roster, excluded = self.get_roster_query_strings(roster, team_id)
    roster_string = str(roster)[1:-1]
    try:
      query = """
        INSERT INTO players {0} VALUES
        {1}
        ON CONFLICT (espn_id)
        DO UPDATE SET
        {0} = {2}
      """.format(keys, roster, excluded)
      cursor = self.connection.cursor()
      cursor.execute(query)
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

  # This function takes a list of player dictionaries and returns strings formatted
  # correctly for use in a postgresql query.

  def get_roster_query_strings(self, roster, team_id):
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
    excluded_string = "("
    for key in keys:
      keys_string += f"{key}, "
      excluded_string += f"EXCLUDED.{key}, "
    keys_string += "team_id)"
    excluded_string += "EXCLUDED.team_id)"
    keys_string = replace_keys(keys_string)
    excluded_string = replace_keys(excluded_string)
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
          value = player[key]
          value = value.replace("'", "''") if isinstance(value, str) else value
          player_list.append(value)
      player_list.append(team_id)
      player_tuple = tuple(player_list)
      roster_tuples.append(player_tuple)
      roster = tuple(roster_tuples)
      roster_string = str(roster)[1:-1]
      roster_string = roster_string.replace("None", "null")
      roster_string = roster_string.replace('"', "'")
    return keys_string, roster_string, excluded_string