import requests
from bs4 import BeautifulSoup

from scraper.https_service import HTTPSService

class Client:
  
  def schedule(self):
    service = HTTPSService()
    games = service.schedule()
    return games