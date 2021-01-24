class Processor:
  def format_roster(self, roster):
    formatted_roster = []
    for player in roster:
      name = player["name"].split(" ", 1)
      height = player["height"].split("'")
      weight = player["weight"].split(" ")
      height = (int(height[0]) * 12) + int(height[1][:-1])
      player["first_name"] = name[0]
      player["last_name"] = name[1]
      player["height"] = height
      player["weight"] = int(weight[0]) if weight[0].isnumeric() else None
      formatted_roster.append(player)
    return formatted_roster