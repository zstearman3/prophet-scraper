def convert_height(height):
  try:
    height = height.split("'")
    height = (int(height[0]) * 12) + int(height[1][:-1])
    return height
  except:
    return None

def convert_weight(weight):
  weight = weight.split(" ")
  weight = int(weight[0]) if weight[0].isnumeric() else None
  return weight

def get_espn_id(espn_url):
  espn_id = espn_url.split("id/")
  espn_id = espn_id[1]
  espn_id = espn_id.split("/")
  espn_id = espn_id[0]
  return espn_id

def parse_makes_attempts(value_string):
  values = value_string.split("-")
  makes = values[0]
  attempts = values[1]
  return makes, attempts

class Processor:
  def format_roster(self, roster):
    formatted_roster = []
    for player in roster:
      name = player["name"].split(" ", 1)
      player["first_name"] = name[0]
      player["last_name"] = name[1]
      player["height"] = convert_height(player["height"])
      player["weight"] = convert_weight(player["weight"])
      player["espn_id"] = get_espn_id(player["espn_url"])
      formatted_roster.append(player)
    return formatted_roster

  def get_espn_id(self, game):
    espn_id = game['uid'].split("~e:", 1)[1]
    return espn_id

  def parse_team_game(self, team_game, team_id):
    team_game_record = {}
    team_game_record["team_id"] = team_id
    for stat in team_game["statistics"]:
      if stat["label"] == "FG":
        team_game_record["field_goals_made"], team_game_record["field_goals_attempted"] = (
          parse_makes_attempts(stat["displayValue"]))
      if stat["label"] == "3PT":
        team_game_record["three_pointers_made"], team_game_record["three_pointers_attempted"] = (
          parse_makes_attempts(stat["displayValue"]))
      if stat["label"] == "FT":
        team_game_record["free_throws_made"], team_game_record["free_throws_attempted"] = (
          parse_makes_attempts(stat["displayValue"]))
      if stat["label"] == "Rebounds":
        team_game_record["rebounds"] = stat["displayValue"]
    print(team_game_record)
    return team_game_record

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

    return home_team_game_record, away_team_game_record

  def process_game_details(self, game, id_dictionary):
    game_record = {}
    header = game["header"]
    competition = header["competitions"][0]
    home_team = competition["competitors"][0]
    away_team = competition["competitors"][1]
    game_record["espn_id"] = header["id"]
    game_record["is_tournament"] = header["league"]["isTournament"]
    game_record["neutral_site"] = competition["neutralSite"]
    game_record["status"] = competition["status"]["type"]["description"]
    game_record["date"] = competition["date"]
    game_record["in_conference"] = competition["conferenceCompetition"]
    game_record["home_team_espn_id"] = home_team["id"]
    game_record["home_team_score"] = home_team["score"]
    if "linescores" in home_team :
      game_record["home_team_first_half_score"] = home_team["linescores"][0]["displayValue"]
      game_record["home_team_second_half_score"] = home_team["linescores"][1]["displayValue"]
    game_record["away_team_espn_id"] = away_team["id"]
    game_record["away_team_score"] = away_team["score"]
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

    return(game_record)