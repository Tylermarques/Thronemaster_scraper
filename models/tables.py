from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import re
from datetime import datetime

Base = declarative_base()


class Game(Base):
    __tablename__ = 'games'

    def __init__(self):
        super().__init__()
        self.players = {}

    def __repr__(self):
        return f"<Game id={self.id} players={self.players}>"

    id = Column(Integer, primary_key=True)  # Game id as given by ThroneMaster
    game_id = Column(Integer, unique=True)
    second_edition = Column(Boolean, default=True)  # Is game in second edition?
    aborted = Column(Boolean, default=False)  # Was game aborted for any reason?
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    end_turn = Column(Integer)
    winner = Column(Integer, ForeignKey('users.id'))
    moves = relationship('Move', back_populates='game')
    users = relationship('User_Game', back_populates='game')

    def parse(self, session, review=None, log=None):
        self.game_id = int(re.search(r'(Events of Game )([0-9]+).+', log.find('h4').text).group(2))
        print(self.game_id)
        if not review and not log:
            raise ValueError("Must provide at least one soup")
        if review:
            self.house_search(review.find_all('a', {'title': 'Go to player\'s profile'}), session)
        if log:
            self.get_moves(log, session)
        return self

    def house_search(self, user_tags, session):

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
            result = session.query(User).filter(User.username == user_name).first()
            if result:
                return result
            else:
                user.username = user_name
                session.add(user)
                result = session.query(User).filter(User.username == user_name).first()
                return result

        session.add(self)
        for tag in user_tags:
            user_game = User_Game()
            _house = check_attrs_for_house(tag.span.attrs)
            _user_name = tag.span.text.strip()
            user = get_user_id(_user_name, session)
            self.players[_house] = user
            user_game.user_id = int(user.id)
            user_game.game_id = self.id
            user_game.house = _house
            session.add(user_game)

    def get_moves(self, soup, session):

        def determine_winner(game, string):
            user_names = {}
            for user_game in game.users:
                user_names[user_game.user.username] = user_game.user
            for user_name in user_names.keys():
                if user_name in string:
                    return user_names[user_name]
            raise ValueError

        def determine_house(string):
            houses = ['Lannister', 'Tyrell', 'Stark', 'Greyjoy', 'Martell', 'Baratheon']
            if string:
                string_houses = []
                for house in houses:
                    if house in string:
                        string_houses.append(house)
                house_dict = {string_houses.index(house): house for house in string_houses}
                if not house_dict:
                    return None
                return house_dict[min(house_dict.keys())]

        def determine_areas(string):
            # FIXME What if there is a march to multiple locations?
            # TODO Order locations in order of appearance in string
            areas = ['Port of Winterfell', 'Port of Lannisport', 'Port of Dragonstone', 'Port of White Harbor',
                     'Bay of Ice', 'Sunset Sea', "Ironman's Bay", 'The Golden Sound', 'West Summer Sea',
                     'Redwyne Straights', 'East Summer Sea', 'Sea of Dorne', 'Shipbreaker Bay', 'Blackwater Bay',
                     'The Narrow Sea', 'The Shivering Sea', 'Castle Black', 'Winterfell', 'Karhold', 'The Stony Shore',
                     'White Harbor', "Widow's Watch", 'Moat Cailin', 'Greywater Watch', "Flint's Finger", 'The Twins',
                     'Seagard', 'The Fingers', 'The Mountains of the Moon', 'Riverrun', 'The Eyrie', 'Lannisport',
                     'Harrenhal', 'Stoney Sept', 'Crackclaw Point', 'Dragonstone', 'Blackwater', "King's Landing",
                     'Searoad Marches', 'Kingswood', 'The Reach', 'The Arbor']
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

        def house_to_user_id(game, house):
            if not house:
                return
            user_houses = {}
            for user_game in game.users:
                user_houses[user_game.house.lower()] = user_game.user
            return user_houses.get(house.lower()).id

        move_table = soup.find('table', {'style': 'font-size:small'})
        tags = move_table.find_all(lambda _: _.name == 'tr' and len(_.contents) == 13)
        for tag in tags[1:]:
            move = Move(game_id=self.id)
            tds = tag.find_all('td')
            ths = tag.find_all('th')
            move.move_number = int(tds[0].text)
            move.turn_number = int(ths[0].text)
            move.phase = ths[1].text
            move.log_entry = tds[2].text
            move.date = datetime.strptime(tds[-1].text, '%Y-%b-%d, %H:%M')
            if 'GAME ABORTED' in move.log_entry:
                self.aborted = True
                session.add(move)
                return self
            # move.house =
            if not self.start_date or self.start_date < move.date:
                self.start_date = move.date
            # Reasons to skip
            #    Any consolidate power that isn't mustering

            if move.phase == 'PLANNING':
                pass
            elif move.phase == 'MARCH':
                if 'Battle!' in move.log_entry:
                    continue
                else:
                    areas = determine_areas(move.log_entry)
                    units = determine_units(move.log_entry)
                    if areas:
                        move.start_location = areas[0]
                        move.end_location = areas[-1]
                if units:
                    setattr(move, units[1], units[0])

            elif move.phase == 'BATTLE':
                continue
            elif move.phase == 'RAID':
                continue
            elif move.phase == 'RAVEN':
                if not move.user_id:
                    continue
            elif move.phase == 'POWER':
                if "consolidate" in move.log_entry.lower():
                    continue
                units = determine_units(move.log_entry)
                setattr(move, units[1], units[0])

            elif move.phase == 'WESTEROS':
                continue
                if 'The holder of the Iron Throne chose the following event:' in move.log_entry:
                    continue
                pass
            elif move.phase == 'GAME END':
                # TODO determine username
                self.winner = determine_winner(self, move.log_entry).id
                self.end_turn = move.turn_number
                self.end_date = move.date
                continue

                # self.house =
            else:  # What if nothing works?
                continue
            move.user_id = house_to_user_id(self, determine_house(move.log_entry))
            # print(move.describe())
            if not move.user_id:
                raise ValueError('wtf guys')
            session.add(move)

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



