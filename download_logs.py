import requests
from progress.bar import Bar
import time
import random


def downloader(url):
    file_name = 'game_logs/' + str(url[url.find('game=')+5:].split('&')[0])
    r = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(r.content)


if __name__ == '__main__':
    id_list = [x for x in range(100040, 100049)]
    urls = [f'http://game.thronemaster.net/?game={game_log_id}&show=log' for game_log_id in id_list]

    bar = Bar('Processing', max=len(urls))
    for url in urls:
        downloader(url)
        bar.next()
        time.sleep(random.randint(0, 3) + (random.randint(1,10)/10))
    bar.finish()


