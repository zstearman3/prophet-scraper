import processor_helpers

class RosterProcessor:
  def format_roster(self, roster):
    formatted_roster = []
    for player in roster:
      name = player["name"].split(" ", 1)
      player["first_name"] = name[0]
      player["last_name"] = name[1]
      player["height"] = processor_helpers.convert_height(player["height"])
      player["weight"] = processor_helpers.convert_weight(player["weight"])
      player["espn_id"] = processor_helpers.get_espn_id(player["espn_url"])
      formatted_roster.append(player)
    return formatted_roster
