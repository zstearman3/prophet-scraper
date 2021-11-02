from datetime import datetime
import scraper.processor_helpers as processor_helpers
import scraper.processor_validators as processor_validators
from stat_calculator.team_game_calculator import TeamGameCalculator

class ScheduleProcessor:
  def parse_team_game(self, team_game, team_id):
    team_game_record = {}
    team_game_record["team_id"] = team_id
    for stat in team_game["statistics"]:
      if stat["label"] == "FG":
        team_game_record["field_goals_made"], team_game_record["field_goals_attempted"] = (
          processor_helpers.parse_makes_attempts(stat["displayValue"]))
      elif stat["label"] == "3PT":
        team_game_record["three_pointers_made"], team_game_record["three_pointers_attempted"] = (
          processor_helpers.parse_makes_attempts(stat["displayValue"]))
      elif stat["label"] == "FT":
        team_game_record["free_throws_made"], team_game_record["free_throws_attempted"] = (
          processor_helpers.parse_makes_attempts(stat["displayValue"]))
      elif stat["label"] == "Rebounds":
        team_game_record["rebounds"] = stat["displayValue"]
      elif stat["label"] == "Offensive Rebounds":
        team_game_record["offensive_rebounds"] = stat["displayValue"]
      elif stat["label"] == "Defensive Rebounds":
        team_game_record["defensive_rebounds"] = stat["displayValue"]
      elif stat["label"] == "Assists":
        team_game_record["assists"] = stat["displayValue"]
      elif stat["label"] == "Steals":
        team_game_record["steals"] = stat["displayValue"]
      elif stat["label"] == "Blocks":
        team_game_record["blocks"] = stat["displayValue"]
      elif stat["label"] == "Turnovers":
        team_game_record["turnovers"] = stat["displayValue"]
      elif stat["label"] == "Fouls":
        team_game_record["fouls"] = stat["displayValue"]
      elif stat["label"] == "Technical Fouls":
        team_game_record["technical_fouls"] = stat["displayValue"]
      elif stat["label"] == "Flagrant Fouls":
        team_game_record["flagrant_fouls"] = stat["displayValue"]
      elif stat["label"] == "Largest Lead":
        team_game_record["largest_lead"] = stat["displayValue"]
    return team_game_record

  def set_home_points(self, game_record):
    game_record["points"] = self.home_team_score
    game_record["points_allowed"] = self.away_team_score
    return game_record

  def set_away_points(self, game_record):
    game_record["points"] = self.away_team_score
    game_record["points_allowed"] = self.home_team_score
    return game_record

  def get_team_game_records(self, box_score, home_espn_id, away_espn_id, home_id, away_id):
    home_team_game_record = {}
    away_team_game_record = {}
    team_box_score_1 = box_score[0]
    team_box_score_2 = box_score[1]

    if team_box_score_1["team"]["id"] == away_espn_id:
      away_team_game_record = self.parse_team_game(team_box_score_1, away_id)
    elif team_box_score_1["team"]["id"] == home_espn_id:
      home_team_game_record = self.parse_team_game(team_box_score_1, home_id)

    if team_box_score_2["team"]["id"] == away_espn_id:
      away_team_game_record = self.parse_team_game(team_box_score_2, away_id)
    elif team_box_score_2["team"]["id"] == home_espn_id:
      home_team_game_record = self.parse_team_game(team_box_score_2, home_id)

    away_team_game_record["home_game"] = False
    home_team_game_record["home_game"] = True
    away_team_game_record["neutral_game"] = self.neutral_site
    home_team_game_record["neutral_game"] = self.neutral_site
    away_team_game_record["game_espn_id"] = self.game_espn_id
    home_team_game_record["game_espn_id"] = self.game_espn_id

    home_team_game_record = self.set_home_points(home_team_game_record)
    away_team_game_record = self.set_away_points(away_team_game_record)

    home_team_game_record = processor_validators.validate_game_record(home_team_game_record)
    away_team_game_record = processor_validators.validate_game_record(away_team_game_record)

    return home_team_game_record, away_team_game_record


  def process_team_scores(self, game_record, home_team, away_team):
    self.home_team_score = home_team["score"]
    self.away_team_score = away_team["score"]

    game_record["home_team_score"] = self.home_team_score
    game_record["away_team_score"] = self.away_team_score

    if "linescores" in home_team :
      game_record["home_team_first_half_score"] = home_team["linescores"][0]["displayValue"]
      game_record["home_team_second_half_score"] = home_team["linescores"][1]["displayValue"]

    if "linescores" in away_team :
      game_record["away_team_first_half_score"] = away_team["linescores"][0]["displayValue"]
      game_record["away_team_second_half_score"] = away_team["linescores"][1]["displayValue"]

    if int(game_record["home_team_score"]) > 0 and int(game_record["away_team_score"]) > 0:
      if game_record["home_team_score"] > game_record["away_team_score"]:
        game_record["home_team_winner"] = True
        game_record["away_team_winner"] = False
      elif game_record["away_team_score"] > game_record["home_team_score"]:
        game_record["home_team_winner"] = False
        game_record["away_team_winner"] = True

    return game_record

  def process_game_details(self, game, id_dictionary):
    game_record = {}
    header = game["header"]
    competition = header["competitions"][0]
    home_team = competition["competitors"][0]
    away_team = competition["competitors"][1]

    self.neutral_site = competition["neutralSite"]
    self.game_espn_id = header["id"]
    game_record = self.process_team_scores(game_record, home_team, away_team)

    game_record["espn_id"] = self.game_espn_id
    game_record["is_tournament"] = header["league"]["isTournament"]
    game_record["neutral_site"] = competition["neutralSite"]
    game_record["status"] = competition["status"]["type"]["description"]
    game_record["date"] = competition["date"]
    game_record["in_conference"] = competition["conferenceCompetition"]
    game_record["home_team_espn_id"] = home_team["id"]
    game_record["away_team_espn_id"] = away_team["id"]

    if int(game_record["home_team_espn_id"]) in id_dictionary.keys():
      game_record["home_team_id"] = id_dictionary[int(game_record["home_team_espn_id"])]
    else:
      game_record["home_team_id"] = None
    if int(game_record["away_team_espn_id"]) in id_dictionary.keys():
      game_record["away_team_id"] = id_dictionary[int(game_record["away_team_espn_id"])]
    else:
      game_record["away_team_id"] = None

    home_team_game_record, away_team_game_record = self.get_team_game_records(game["box_score"]["teams"],
                                                    game_record["home_team_espn_id"],
                                                    game_record["away_team_espn_id"],
                                                    game_record["home_team_id"],
                                                    game_record["away_team_id"])

    if away_team_game_record != None:
      home_team_game_record["opponent_game"] = away_team_game_record
    if home_team_game_record != None:
      away_team_game_record["opponent_game"] = home_team_game_record

    return(game_record, home_team_game_record, away_team_game_record)

  def prepare_team_games(self, team_games, id_dictionary):
    for team_game in team_games:
      if int(team_game["game_espn_id"]) in id_dictionary.keys():
        team_game["game_id"] = id_dictionary[int(team_game["game_espn_id"])]
      else:
        print(f"Could not find game with id={team_game['game_espn_id']}")

      calculator = TeamGameCalculator(team_game)
      team_game = calculator.prepare_team_game()
      team_game = self._set_timestamps(team_game)

    return team_games

  def get_espn_id_from_uid(self, game):
    espn_id = game['uid'].split("~e:", 1)[1]
    return espn_id

  def _set_timestamps(self, game):
    time = datetime.now()
    game["created_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
    game["updated_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
    return game