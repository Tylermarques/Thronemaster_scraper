"""
Throne Master Parsing Script - Models
It's not pretty, but it's mine.

Used to create the database objects used to commit data from logs to postgres.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import re
from datetime import datetime

Base = declarative_base()


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)  # Game id as given by ThroneMaster
    thronemaster_id = Column(Integer, unique=True)
    second_edition = Column(Boolean, default=True)  # Is game in second edition?
    aborted = Column(Boolean, default=False)  # Was game aborted for any reason?
    game_type = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    end_turn = Column(Integer)
    winner = Column(Integer, ForeignKey('users.id'))
    moves = relationship('Move', back_populates='game')
    users = relationship('User_Game', back_populates='game')

    def __init__(self):
        super().__init__()
        self.players = {}
        self.still_running = True
        self.locations = {'left: 225px; top: 205px;': 'Port of Winterfell',
                          'left: 50px; top: 895px;': 'Port of Lannisport',
                          'left: 652px; top: 930px;': 'Port of Dragonstone',
                          'left: 440px; top: 526px;': 'Port of White Harbor',
                          'left: 55px; top: 200px;': 'Bay of Ice', 'left: 2px; top: 543px;': 'Sunset Sea',
                          'left: 12px; top: 625px;': "Ironman's Bay", 'left: 20px; top: 830px;': 'The Golden Sound',
                          'left: 180px; top: 1335px;': 'West Summer Sea',
                          'left: 25px; top: 1150px;': 'Redwyne Straights',
                          'left: 670px; top: 1095px;': 'East Summer Sea',
                          'left: 490px; top: 1355px;': 'East Summer Sea', 'left: 550px; top: 1180px;': 'Sea of Dorne',
                          'left: 670px; top: 1020px;': 'Shipbreaker Bay', 'left: 527px; top: 848px;': 'Blackwater Bay',
                          'left: 655px; top: 590px;': 'The Narrow Sea', 'left: 655px; top: 295px;': 'The Shivering Sea',
                          'left: 355px; top: 91px;': 'Castle Black', 'left: 400px; top: 245px;': 'Winterfell',
                          'left: 536px; top: 262px;': 'Karhold',
                          'left: 165px; top: 315px;': 'The Stony Shore', 'left: 447px; top: 365px;': 'White Harbor',
                          "left: 490px; top: 435px;": "Widow's Watch", 'left: 345px; top: 470px;': 'Moat Cailin',
                          'left: 162px; top: 488px;': 'Greywater Watch', "left: 58px; top: 533px;": "Flint's Finger",
                          'left: 320px; top: 575px;': 'The Twins',
                          'left: 204px; top: 628px;': 'Seagard', 'left: 520px; top: 575px;': 'The Fingers',
                          'left: 550px; top: 640px;': 'The Mountains of the Moon',
                          'left: 260px; top: 695px;': 'Riverrun',
                          'left: 538px; top: 722px;': 'The Eyrie', 'left: 160px; top: 766px;': 'Lannisport',
                          'left: 375px; top: 795px;': 'Harrenhal',
                          'left: 219px; top: 903px;': 'Stoney Sept', 'left: 540px; top: 795px;': 'Crackclaw Point',
                          'left: 593px; top: 860px;': 'Dragonstone', 'left: 221px; top: 958px;': 'Blackwater',
                          "left: 450px; top: 890px;": "King's Landing", 'left: 105px; top: 955px;': 'Searoad Marches',
                          'left: 531px; top: 960px;': 'Kingswood', 'left: 275px; top: 990px;': 'The Reach',
                          'left: 30px; top: 1295px;': 'The Arbor',
                          'left: 131px; top: 1068px;': 'Highgarden', 'left: 590px; top: 1220px;': 'Sunspear',
                          'left: 395px; top: 1310px;': 'Salt Shore',
                          'left: 225px; top: 1135px;': 'Dornish Marches',
                          'left: 295px; top: 1115px;': 'Dornish Marches', 'left: 125px; top: 1245px;': 'Three Towers',
                          'left: 75px; top: 1195px;': 'Oldtown', 'left: 435px; top: 1115px;': 'Storms End',
                          'left: 220px; top: 1300px;': 'Starfall', 'left: 76px; top: 1087px;': 'Port of Oldtown',
                          'left: 143px; top: 648px;': 'Pyke', 'left: 19px; top: 745px;': 'Port of Pyke',
                          'left: 165px; top: 1340px;': 'West Summer Sea'}

    def __repr__(self):
        return f"<Game id={self.id} players={self.players}>"

    def parse(self, session, review=None, log=None):
        session.add(self)
        self.thronemaster_id = int(re.search(r'(Events of Game )([0-9]+).+', log.find('h4').text).group(2))
        self.game_type = log.find_all('table')[-1].text.strip()
        if not review and not log:
            raise ValueError("Must provide at least one soup")
        if review:
            self.parse_review(review, session)
        if log:
            self._log_parser(log, session)
        return self

    def parse_review(self, soup, session):
        def _old_review_parser(game, user_tags, session):

            def check_attrs_for_house(attrs):
                house_name_colours = {
                    'color-B': 'Baratheon',
                    'color-L': 'Lannister',
                    'color-M': 'Martell',
                    'color-G': 'Greyjoy',
                    'color-S': 'Stark',
                    'color-T': 'Tyrell'
                }

                for key, value in attrs.items():
                    if key == 'class':
                        if isinstance(attrs[key], list):
                            for i in value:
                                if 'color' in i:
                                    return house_name_colours[i]
                        else:
                            if 'color' in value:
                                return house_name_colours[attrs[key]]
                return None

            def get_user_id(user_name, session):
                user = User()
                session.add(user)
                result = session.query(User).filter(User.username == user_name).first()
                if result:
                    return result
                else:
                    user.username = user_name
                    result = session.query(User).filter(User.username == user_name).first()
                    return result

            # Associate games with users and houses
            for tag in user_tags:
                user_game = User_Game()
                session.add(user_game)
                _house = check_attrs_for_house(tag.span.attrs)
                _user_name = re.search('(?:[a-zA-Z:\/\/\.=&]+)(?:&usr=([\S]+))', tag.attrs['href']).groups(1)[
                    0].replace(
                    '%20', ' ').strip()
                user = get_user_id(_user_name, session)
                game.players[_house] = user
                user_game.user_id = int(user.id)
                user_game.game_id = game.id
                user_game.house = _house

        _old_review_parser(self, soup.find_all('a', {'title': 'Go to player\'s profile'}), session)

        def get_user_obj(game, house):
            _dict = {x.house: x for x in game.users}
            return _dict[house]

        order_tags = soup.find_all(lambda tag: tag.name == 'div'
                                               and 'Order Token' in str(tag.get('title'))
                                               and tag.get('style') != "left: -1250px; top: 0px;")
        for tag in order_tags:
            order = StartingOrder()
            session.add(order)
            user = get_user_obj(self, tag.attrs['title'].split()[-1])
            order.user_id = user.id
            order.game_id = self.id
            order.order = tag.attrs['class'][1]
            try:
                order.area = self.locations[str(tag.attrs['style'])]
            except KeyError as e:
                print('\n ****** KEYERROR *****')
                print(e)
                print('*' * 8 + '\n')


    def _log_parser(self, soup, session):

        def determine_areas(game, string):
            # FIXME What if there is a march to multiple locations?
            areas = list(game.locations.values())
            move_areas = []
            for area in areas:
                if area in string:
                    move_areas.append(area)
            move_areas.sort(key=lambda x: string.find(x))
            return move_areas

        def determine_units(string):
            unit_types = ['Knights', 'Footmen', 'Siege', 'Ships']
            for unit in unit_types:
                if unit in string:
                    return int(re.search('([0-9])', string).group(0)), unit.lower()

        def determine_user_id(game, move):
            """
            Args:
                game (Game):
                move (Move):
                house (str):

            Returns:
                int: User ID
            """

            def determine_winner(game, string):
                user_names = {}
                for user_game in game.users:
                    user_names[user_game.user.username] = user_game.user
                for user_name in user_names.keys():
                    if user_name in string:
                        return user_names[user_name]
                return None

            def determine_house(string):
                houses = ['Lannister', 'Tyrell', 'Stark', 'Greyjoy', 'Martell', 'Baratheon']
                if string:
                    string_houses = []
                    for _house in houses:
                        if _house in string:
                            string_houses.append(_house)
                    house_dict = {string_houses.index(house): house for house in string_houses}
                    if not house_dict:
                        return None
                    return house_dict[min(house_dict.keys())]

            house = determine_house(move.log_entry)
            if house:
                user_houses = {}
                for user_game in game.users:
                    user_houses[user_game.house.lower()] = user_game.user
                return user_houses.get(house.lower()).id
            else:
                user = determine_winner(game, move.log_entry)
                if user:
                    return user.id
                return None

        move_table = soup.find('table', {'style': 'font-size:small'})
        tags = move_table.find_all(lambda _: _.name == 'tr' and len(_.contents) == 13)
        for tag in tags[1:]:
            move = Move(game_id=self.id)
            session.add(move)
            tds = tag.find_all('td')
            ths = tag.find_all('th')
            move.move_number = int(tds[0].text)
            move.turn_number = int(ths[0].text)
            move.phase = ths[1].text
            move.log_entry = tds[2].text
            move.date = datetime.strptime(tds[-1].text, '%Y-%b-%d, %H:%M')
            move.user_id = determine_user_id(self, move)
            if 'GAME ABORTED' in move.log_entry:
                self.end_turn = move.turn_number
                self.aborted = True
                self.end_date = move.date
                return self
            # move.house =
            if not self.start_date:
                self.start_date = move.date
            # Reasons to skip
            #    Any consolidate power that isn't mustering

            if move.phase == 'PLANNING':
                pass
            elif move.phase == 'MARCH':
                units = []
                if 'Battle!' in move.log_entry:
                    pass
                else:
                    areas = determine_areas(self, move.log_entry)
                    units = determine_units(move.log_entry)
                    if areas:
                        move.start_location = areas[0]
                        move.end_location = areas[-1]
                if units and move:
                    try:
                        setattr(move, units[1], units[0])
                    except:
                        print('\n ***********\nSomething wrong with the units thing \n**********')

            elif move.phase == 'BATTLE':
                pass
            elif move.phase == 'RAID':
                pass
            elif move.phase == 'RAVEN':
                if not move.user_id:
                    pass
                pass
            elif move.phase == 'POWER':
                if "consolidate" in move.log_entry.lower():
                    pass
                else:
                    units = determine_units(move.log_entry)
                if units:
                    setattr(move, units[1], units[0])

            elif move.phase == 'WESTEROS':
                if 'The holder of the Iron Throne chose the following event:' in move.log_entry:
                    pass
                pass
            elif move.phase == 'GAME END':
                # TODO if no game end tag, don't add game to db
                self.winner = determine_user_id(self, move)
                self.end_turn = move.turn_number
                self.end_date = move.date
                self.still_running = False

                # self.house =
            else:  # What if nothing works?
                pass

            # print(move.describe())
            # if not move.user_id:
            #     raise ValueError('No user id in Move')
            if not move.game_id:
                raise ValueError('No game id in Move')
            if not move.phase:
                raise ValueError('No phase in move')

            # print(f'Turn Number: {move.turn_number}\nPhase: {move.phase}\nHouse={determine_house(move.log_entry)}')
            # print(move)

        # print(tags)


class Move(Base):
    def __repr__(self):
        return f'<Move id={self.id} move_number={self.move_number}>'

    __tablename__ = 'moves'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(Integer, ForeignKey('users.id'))
    move_number = Column(Integer)
    turn_number = Column(Integer)
    phase = Column(String)
    knights = Column(Integer)
    siege = Column(Integer)
    footmen = Column(Integer)
    ships = Column(Integer)
    start_location = Column(String)
    end_location = Column(String)
    log_entry = Column(String)
    date = Column(DateTime)
    game = relationship('Game', back_populates='moves')

    def units(self):
        return f'{{\n' \
               f'    Knights: {self.knights}\n' \
               f'    Siege: {self.siege}\n' \
               f'    Footmen: {self.footmen}\n' \
               f'    Ships: {self.ships}\n' \
               f'}}'

    def describe(self):
        return f'{{\n' \
               f'  Turn: {self.turn_number}\n' \
               f'  Phase: {self.phase}\n' \
               f'  User ID: {self.user_id}\n' \
               f'  Date: {self.date}\n' \
               f'  Start Location: {self.start_location}\n' \
               f'  End Location: {self.end_location}\n' \
               f'  Units: {{\n' \
               f'    Knights: {self.knights}\n' \
               f'    Siege: {self.siege}\n' \
               f'    Footmen: {self.footmen}\n' \
               f'    Ships: {self.ships}\n' \
               f'  }}\n' \
               f'  Log Entry: {self.log_entry}\n' \
               f'}}'


class User(Base):
    def __repr__(self):
        return f'<User username={self.username}>'

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    games = relationship('User_Game', back_populates='user')


class User_Game(Base):
    __tablename__ = 'user_games'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    house = Column(String)

    game = relationship('Game', back_populates='users')
    user = relationship('User', back_populates='games')


class StartingOrder(Base):
    __tablename__ = 'starting_moves'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    user_id = Column(Integer)
    area = Column(String)
    order = Column(String)
