from scraper.client import Client
from scraper.processor import Processor

client = Client()
rosters = client.rosters()
processor = Processor()
for id, roster in rosters.items():
  roster = processor.format_roster(roster)
  # TODO: Add roster to db
print(roster)
