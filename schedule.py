from scraper.client import Client

client = Client()
games = client.schedule()

for game in games:
  print(game)