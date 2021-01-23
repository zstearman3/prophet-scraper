from scraper.client import Client

client = Client()
rosters = client.rosters()

print(rosters)