import requests
from multiprocessing.dummy import Pool as ThreadPool
import time
import os

def downloader(game_log_id):
    if game_log_id % 100 == 0:
        print(f'Downloading log {game_log_id} ... ', end='')

    url = f'http://game.thronemaster.net/?game={game_log_id}&show=log'
    try:
        file_name = 'game_logs/' + str(url[url.find('game=')+5:].split('&')[0])
        r = requests.get(url)
        with open(file_name, 'wb') as file:
            file.write(r.content)
    except Exception as e:
        if game_log_id % 100 == 0:
            print('FAILED')
            print(e)
    time.sleep(0.33)
    if game_log_id % 100 == 0:
        print('finished')
    return

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f

if __name__ == '__main__':
    pool = ThreadPool(4)
    game_ids = range(80000,140000)
    downloaded_logs = listdir_nohidden(os.getcwd()+'/game_logs/')
    downloaded_logs = [int(log) for log in downloaded_logs]
    game_ids = [x for x in game_ids if x not in downloaded_logs]
    print(len(game_ids))
    results = pool.map(downloader, game_ids)