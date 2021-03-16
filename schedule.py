from scraper.client import Client
from scraper.processor import Processor

client = Client()
processor = Processor()
games = client.schedule()
for game in games:
  processed_game = processor.process_game_details(game)
