from bs4 import BeautifulSoup
from models.tables import Game, User, Move
from models import Session, engine


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
    game_id = 106230
    with open(f'game_logs/{game_id}') as game_log_file:
        with open(f'reviews/{game_id}') as review_file:
            session = Session()
            game_log = BeautifulSoup(game_log_file, 'html.parser')
            review = BeautifulSoup(review_file, 'html.parser')
            game = Game().parse(session, review=review, log=game_log)
            session.commit()
            print('hey')