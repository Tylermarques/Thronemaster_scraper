from bs4 import BeautifulSoup
from models.tables import Game
from models import Session
import os


def main(start, end):
    session = Session()
    id_list = [x for x in range(start, end)]
    for game_id in id_list:
        try:
            with open(f'reviews/{game_id}') as review_file:
                clean = review_file.read()
                review = BeautifulSoup(clean, 'html.parser')
                game = Game().parse(review, session)
                print(game)

            with open(f'game_logs/{game_id}') as game_log_file:
                game_log = BeautifulSoup(game_log_file, 'html.parser')

        except EnvironmentError:
            with open('parse_errors.txt', 'a') as error_log:
                error_log.write(f'{game_id}\n')
                print(f'Error with id {game_id}')

if __name__ == '__main__':
    i = 0
    for game_id in os.listdir('game_logs/'):
        i += 1
        if i > 100:
            break
        with open(f'game_logs/{game_id}') as game_log_file:
                with open(f'reviews/{game_id}') as review_file:
                    try:
                        session = Session()
                        game_log = BeautifulSoup(game_log_file, 'html.parser')
                        review = BeautifulSoup(review_file, 'html.parser')
                        game = Game().parse(session, review=review, log=game_log)
                        session.commit()
                        if int(i) % 20 == 0:
                            print(f'Finished game id {game_id}')
                    except:
                        with open('logs/parse_errors.txt', 'a') as log:
                            log.write(game_id + '\n')


# if __name__ == '__main__':
#     game_id = 106230
#     with open(f'game_logs/{game_id}') as game_log_file:
#         with open(f'reviews/{game_id}') as review_file:
#             session = Session()
#             game_log = BeautifulSoup(game_log_file, 'html.parser')
#             review = BeautifulSoup(review_file, 'html.parser')
#             game = Game().parse(session, review=review, log=game_log)
#             session.commit()
