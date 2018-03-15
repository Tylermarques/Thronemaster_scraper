from bs4 import BeautifulSoup
from models import Game, Session, Base, engine
import os
import sys
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f


def determine_downloads(path, start, end):
    files = set(listdir_nohidden(path))
    full_list = set([str(x) for x in range(start, end)])
    return list(set(full_list) - set(files))


def download_log(game_id):
    url = f'http://game.thronemaster.net/?game={game_id}&show=log'
    r = requests.get(url)
    with open(f'game_logs/{game_id}', 'wb') as file:
        file.write(r.content)
    return r.content


def download_review(game_id):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    url = f'http://game.thronemaster.net/?game={game_id}&review=1'
    browser = webdriver.Chrome(chrome_options=chrome_options)
    file_name = 'reviews/' + str(url[url.find('game=') + 5:].split('&')[0])
    browser.get(url)
    innerHTML = browser.execute_script("return document.body.innerHTML")
    with open(file_name, 'wb') as file:
        file.write(innerHTML.encode('utf-8'))
    browser.close()
    return innerHTML


def parse(game_id, log_file, review_file, session):
    try:
        game_log = BeautifulSoup(log_file, 'html.parser')
        review = BeautifulSoup(review_file, 'html.parser')
        if game_log.text == "ERROR: Invalid Game ID!":
            return
        if review.text == "ERROR: Invalid Game ID!":
            return
        return Game().parse(session, review=review, log=game_log)
    except Exception as e:
        print('\n' + '*' * 10 + f'\n ERROR on ID {game_id}' + '\n' + '*' * 10)
        raise e


def main():
    game_list = range(80000, 140000)
    for game_id in game_list:
        session = Session()
        try:
            review = open(f'reviews/{game_id}')
        except FileNotFoundError:
            review = download_review(game_id)
        try:
            log = open(f'game_logs/{game_id}')
        except FileNotFoundError:
            log = download_log(game_id)
        finally:
            game = parse(game_id, log, review, session)
            if game:
                session.commit()
            else:
                session.rollback()
            session.close()



print('Creating database objects ... ', end='')
Base.metadata.create_all(engine)
print('finished')

if __name__ == '__main__':
    # Read ENV variables
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
            parse(game, session)
        except IntegrityError:
            print('\n****************ERROR EXCEPTED******************\n')
            max_game_id = session.query(func.max(Game.id))
            print(max_game_id.first())

    if env == 'prod':
        main()
