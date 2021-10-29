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

