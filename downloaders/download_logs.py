from progress.bar import Bar
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from models import engine, Session
from bs4 import BeautifulSoup



Base = declarative_base()

class StartingOrder(Base):
    __tablename__ = 'starting_moves'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    area = Column(String)
    order = Column(String)


def downloader(game_log_id):

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    url = f'http://game.thronemaster.net/?game={game_log_id}&show=log'
    try:
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get(url)
        innerHTML = browser.execute_script("return document.body.innerHTML")
        with open(f'reviews/{game_id}', 'wb') as file:
            file.write(innerHTML.encode('utf-8'))
        browser.close()
        return innerHTML
    except Exception as e:
        browser.close()
        print(e)
    time.sleep(0.33)

def parseReview():
    html = downloader(url)



if __name__ == '__main__':
    game_log_id = 106230
    url = f'http://game.thronemaster.net/?game={game_log_id}&review=1'
    downloader(url)