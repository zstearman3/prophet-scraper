def get_game_query_strings(games_array):
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

  query = """
    INSERT INTO games {0} VALUES
    {1}
    ON CONFLICT (espn_id)
    DO UPDATE SET
    {0} = {2}
  """.format(keys_string, games_string, excluded_string)

  return query

def get_team_game_query_strings(games_array):
  keys = (
    "game_espn_id",
    "team_id",
    "game_id",
    "opponent_team_game_id",
    "field_goals_made",
    "field_goals_attempted",
    "field_goal_percentage",
    "three_pointers_made",
    "three_pointers_attempted",
    "three_point_percentage",
    "free_throws_made",
    "free_throws_attempted",
    "free_throw_percentage",
    "rebounds",
    "offensive_rebounds",
    "defensive_rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "fouls",
    "technical_fouls",
    "flagrant_fouls",
    "largest_lead",
    "home_game",
    "neutral_game",
    "points",
    "points_allowed",
    "possessions",
    "offensive_efficiency",
    "defensive_efficiency",
    "assist_rate",
    "allowed_assist_rate",
    "offensive_rebound_rate",
    "defensive_rebound_rate",
    "three_point_proficiency",
    "allowed_three_point_proficiency",
    "created_at",
    "updated_at",
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

  query = """
    INSERT INTO team_games {0} VALUES
    {1}
    ON CONFLICT (team_id, game_id)
    DO UPDATE SET
    {0} = {2}
  """.format(keys_string, games_string, excluded_string)

  return query