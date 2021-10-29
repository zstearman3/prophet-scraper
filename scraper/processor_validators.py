def validate_game_record(game_record):
  if game_record["team_id"] == None:
    return None

  return game_record