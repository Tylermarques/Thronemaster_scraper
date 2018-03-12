from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .tables import Game, Base, User
import sys

env = sys.argv[1] if len(sys.argv) > 2 else 'dev'

if env == 'dev':
    engine = create_engine(f'postgresql://postgres@localhost:5432/game_of_thrones')
else:
    engine = create_engine(f'postgresql://craig:thronemaster@10.50.50.132/game_of_thrones')

Session = sessionmaker(bind=engine)




