import os
import requests
import psycopg2
from psycopg2 import Error
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

  def rosters(self, database="db/prophet_dev", team=None):
    generic_url = HTTPSService.BASE_URL + "/team/roster/_/id/"
    connection = None
    try:
      connection = psycopg2.connect(user="ec2-user",
                                    password = os.getenv('PG_PASSWORD'),
                                    host="127.0.0.1",
                                    port="5432",
                                    database=database)
      cursor = connection.cursor()
      print("PostgreSQL server information")
      print(connection.get_dsn_parameters(), "\n")

      cursor.execute("SELECT * FROM teams")
      record = cursor.fetchone()
    except(Exception, Error) as error:
      print("Error while connecting to PostgreSQL", error)
    finally:
      if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
        return record