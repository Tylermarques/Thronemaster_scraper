from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine(f'postgresql://craig:thronemaster@10.50.50.132/game_of_thrones')
Session = sessionmaker(bind=engine)