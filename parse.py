from bs4 import BeautifulSoup
from models import Game, Session, Base, engine
from multiprocessing.dummy import Pool as ThreadPool
import os


def main(game_id):
    try:
        with open(f'game_logs/{game_id}') as game_log_file:
            with open(f'reviews/{game_id}') as review_file:
                session = Session()
                game_log = BeautifulSoup(game_log_file, 'html.parser')
                review = BeautifulSoup(review_file, 'html.parser')
                Game().parse(session, review=review, log=game_log)
                session.commit()
    except:
        with open('logs/parse_errors.txt', 'a') as log:
            log.write(game_id + '\n')


def main_threaded():
    pool = ThreadPool(4)
    game_ids = list(set(os.listdir('game_logs/')).union(os.listdir('reviews/')))
    print(game_ids)
    # pool.map(main, game_ids)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    main_threaded()

# if __name__ == '__main__':
#     game_id = 106230
#     with open(f'game_logs/{game_id}') as game_log_file:
#         with open(f'reviews/{game_id}') as review_file:
#             session = Session()
#             game_log = BeautifulSoup(game_log_file, 'html.parser')
#             review = BeautifulSoup(review_file, 'html.parser')
#             game = Game().parse(session, review=review, log=game_log)
#             session.commit()
