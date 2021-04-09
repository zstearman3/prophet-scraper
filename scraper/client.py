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
    print(os.getenv('PG_DATABASE'))
    self.connection = psycopg2.connect(user=os.getenv('PG_USER'),
                                       password = os.getenv('PG_PASSWORD'),
                                       host=os.getenv('PG_HOST'),
                                       port="5432",
                                       database=os.getenv('PG_DATABASE'))

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

  def schedule(self, date):
    service = HTTPSService()
    processor = Processor()
    games = service.schedule(date)
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

  def get_all_espn_ids(self):
    espn_ids = self._get_espn_ids()
    id_dictionary = {}
    for team in espn_ids:
      id_dictionary[team[1]] = team[0]
    return id_dictionary

  def get_game_query_strings(self, games_array):
    keys = (
      "espn_id",
      "is_tournament",
      "neutral_site",
      "status",
      "date",
      "in_conference",
      "home_team_id",
      "home_team_score",
      "away_team_id",
      "away_team_score",
      "home_team_first_half_score",
      "home_team_second_half_score",
      "away_team_first_half_score",
      "away_team_second_half_score",
      "home_team_winner",
      "away_team_winner",
    )
    keys_string = "("
    excluded_string = "("
    for key in keys:
      keys_string += f"{key}, "
      excluded_string += f"EXCLUDED.{key}, "
    keys_string = keys_string[:-2]
    excluded_string = excluded_string[:-2]
    keys_string += ")"
    excluded_string += ")"
    games_tuples = []
    for game in games_array:
      game_values = []
      for key in keys:
        value = game[key] if key in game else None
        value = value.replace("'", "''") if isinstance(value, str) else value
        game_values.append(value)
      game_tuple = tuple(game_values)
      games_tuples.append(game_tuple)
    games_tuple = tuple(games_tuples)
    games_string = str(games_tuple)[1:-1]
    games_string = games_string.replace("None", "null")
    games_string = games_string.replace('"', "'")
    return keys_string, games_string, excluded_string

  def update_games(self, games_array):
    keys, games, excluded = self.get_game_query_strings(games_array)
    try:
      query = """
        INSERT INTO games {0} VALUES
        {1}
        ON CONFLICT (espn_id)
        DO UPDATE SET
        {0} = {2}
      """.format(keys, games, excluded)
      cursor = self.connection.cursor()
      cursor.execute(query)
    except(Exception, Error) as error:
      print("Error while connecting to PostgreSQL", error)
    self.connection.commit()
