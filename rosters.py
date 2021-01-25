from scraper.client import Client
from scraper.processor import Processor

client = Client()
rosters = client.get_rosters()
processor = Processor()
for id, roster in rosters.items():
  roster = processor.format_roster(roster)
  client.update_roster(id, roster)
