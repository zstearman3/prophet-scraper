import requests
from bs4 import BeautifulSoup

class HTTPSService:
  BASE_URL = 'https://www.espn.com/mens-college-basketball'
  
  def __init__(self):
    self.name = "CBB Parser"
  
  def schedule(self):
    url = f'{HTTPSService.BASE_URL}/scoreboard'
    page = requests.get(url)
    
    soup = BeautifulSoup(page.content, 'html.parser')
    games = soup.find_all('div', class_='scoreboards')
    
    print(games)
    return games