from scraper.client import Client
from scraper.roster_processor import RosterProcessor

client = Client()
rosters = client.get_rosters()
processor = RosterProcessor()
for id, roster in rosters.items():
  roster = processor.format_roster(roster)
  client.update_roster(id, roster)
