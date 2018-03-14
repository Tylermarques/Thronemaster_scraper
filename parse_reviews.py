from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from models import engine, Session, Game, User
import pprint

Base = declarative_base()


class StartingOrder(Base):
    __tablename__ = 'starting_moves'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    area = Column(String)
    order = Column(String)


def parse_review(game_id, session):
    def get_user_obj(game_id, house, session):
        user = session.query(User).filter(User.games.game_id == game_id) \
                                  .filter(User.games.house == house)
        return user

    def get_game_obj(thronmaster_id, session):
        game = session.query(Game).filter(Game.thronemaster_id == thronmaster_id)
        return game

    order = StartingOrder()
    with open(f'start_moves/{game_id}') as file:
        soup = BeautifulSoup(file, 'html.parser')
        order_tags = soup.find_all(lambda tag: tag.name == 'div'
                                               and 'Order Token' in str(tag.get('title'))
                                               and tag.get('style') != "left: -1250px; top: 0px;")
        pprint.pprint(order_tags)
        game = get_game_obj(game_id, session)
        for tag in order_tags:
            user = get_user_obj(game.id, tag.attrs['title'].split()[-1])
            order.user_id = user.id
            order.game_id = game.id
            order.order = tag.attrs['class'][1]



    session.add()


if __name__ == '__main__':
    parse_review(str(106230), Session())
