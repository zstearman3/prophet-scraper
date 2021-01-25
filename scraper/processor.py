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