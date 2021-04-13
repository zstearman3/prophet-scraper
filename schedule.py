import sys
import getopt
from datetime import datetime
from scraper.client import Client
from scraper.processor import Processor


if __name__ == '__main__':
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]

    short_options = "s:d"
    long_options = ["start_date=", "days="]
    start_date = datetime.strptime("03/02/2021", "%m/%d/%Y")

    try:
        arguements, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    for current_arguement, current_value in arguements:
        if current_arguement in ("-s", "--start_date"):
            start_date = datetime.strptime(current_value, "%m/%d/%Y")

    client = Client()
    processor = Processor()
    games = client.schedule(start_date)
    print(games[0])
    id_dictionary = client.get_all_espn_ids()
    processed_games = []
    for game in games:
        processed_game = processor.process_game_details(game, id_dictionary)
        processed_games.append(processed_game)
    client.update_games(processed_games)