from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
engine = create_engine('postgresql://Tyler@localhost/game_of_thrones')
Session = sessionmaker(bind=engine)




