class Processor:
  def format_roster(self, roster):
    formatted_roster = []
    for player in roster:
      name = player["name"].split(" ", 1)
      player["first_name"] = name[0]
      player["last_name"] = name[1]
      formatted_roster.append(player)
    return formatted_roster