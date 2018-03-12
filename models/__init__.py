from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .tables import Game, Base

# engine = create_engine(f'postgresql://craig:thronemaster@10.50.50.132/game_of_thrones')
engine = create_engine(f'postgresql://postgres@localhost:5432/game_of_thrones')

Session = sessionmaker(bind=engine)




