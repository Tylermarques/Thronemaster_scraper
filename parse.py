from bs4 import BeautifulSoup
from models import Game, Session, Base, engine
from multiprocessing.dummy import Pool as ThreadPool
import os
import sys
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# 11932 Errors on last run
# only 6600 successes

print('Creating database objects ... ', end='')
Base.metadata.create_all(engine)
print('finished')


def main(game_id, session):
    try:
        with open(f'game_logs/{game_id}') as game_log_file:
            with open(f'start_moves/{game_id}') as review_file:
                game_log = BeautifulSoup(game_log_file, 'html.parser')
                review = BeautifulSoup(review_file, 'html.parser')
                Game().parse(session, review=review, log=game_log)
    except Exception as e:
        with open('logs/parse_errors.txt', 'a') as log:
            log.write(str(game_id) + '\n')
    return


def main_threaded():
    pool = ThreadPool(4)
    game_ids = list(set(os.listdir('game_logs/')).union(os.listdir('reviews/')))
    game_ids = sorted(game_ids)
    results = pool.map(main, game_ids)
    return results


if __name__ == '__main__':
    print('Reading env variables ... ', end='')
    if len(sys.argv) < 2:
        raise TypeError("Must specify environment")
    env = sys.argv[1]
    print('finished')

    if env == 'dev':
        print('Opening log files ... ', end='')
        game_id = 106230
        with open(f'game_logs/{game_id}') as game_log_file:
            with open(f'reviews/{game_id}') as review_file:
                print('finished')
                print('Creating session ... ', end='')
                session = Session()
                print('finished')
                print('Souping files ... ', end='')
                game_log = BeautifulSoup(game_log_file, 'html.parser')
                review = BeautifulSoup(review_file, 'html.parser')
                print('finished')

                print('Beginning parsing ... ', end='')
                game = Game().parse(session, review=review, log=game_log)
                print('finished')
                if not game.still_running:
                    print('Commiting session ... ', end='')
                    session.commit()
                    print('finished')
    if env == 'dev2':
        game = 100000
        session = Session()
        try:
            main(game, session)
        except IntegrityError:
            print('\n****************ERROR EXCEPTED******************\n')
            max_game_id = session.query(func.max(Game.id))
            print(max_game_id.first())

    if env == 'prod':
        session = Session()
        game_ids = range(80000, 140000)
        for game in game_ids:
            print(game)
            test_query = session.query(Game).filter(Game.id == int(game)).first()
            if test_query:
                print(f'Game {game} exists, SKIPPING')
            # if max_game_id is not None:
            #     if not isinstance(max_game_id, int):
            #         max_game_id = max_game_id.first()[0]
            #     if int(game) <= max_game_id:
            #         continue
            #     else:
            #         try:
            #             main(game, session)
            #         except IntegrityError:
            #             max_game_id = session.query(func.max(Game.id))
            else:
                try:
                    main(game, session)
                except IntegrityError:
                    print(f'INTEGRITY ERROR ON GAME WITH ID {game}')
            session.commit()
