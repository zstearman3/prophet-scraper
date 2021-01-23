import requests
from bs4 import BeautifulSoup

from scraper.https_service import HTTPSService

class Client:

  def schedule(self):
    service = HTTPSService()
    games = service.schedule()
    return games

  def hierarchy(self):
    service = HTTPSService()

  def rosters(self):
    service = HTTPSService()
    rosters = service.rosters()
    return rosters
