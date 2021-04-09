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

  def process_game_details(self, game, id_dictionary):
    game_record = {}
    home_team_game_record = {}
    away_team_game_record = {}
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
    return(game_record)