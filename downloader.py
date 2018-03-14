from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing.dummy import Pool as ThreadPool
import time


def downloader(game_log_id):
    if game_log_id % 100 == 0:
        print(f'Downloading review {game_log_id} ... ', end='')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    url = f'http://game.thronemaster.net/?game={game_log_id}&review=1'
    try:
        browser = webdriver.Chrome(chrome_options=chrome_options)
        file_name = 'start_moves/' + str(url[url.find('game=') + 5:].split('&')[0])
        browser.get(url)
        innerHTML = browser.execute_script("return document.body.innerHTML")
        with open(file_name, 'wb') as file:
            file.write(innerHTML.encode('utf-8'))
            file.close()
        browser.close()
    except Exception as e:
        if game_log_id % 100 == 0:
            print('FAILED')
        browser.close()
        try:
            file.close()
        except:
            pass
        print(e)
    time.sleep(0.33)
    if game_log_id % 100 == 0:
        print('finished')
    return


if __name__ == '__main__':
    pool = ThreadPool(4)
    game_ids = range(101589, 140000)
    results = pool.map(downloader, game_ids)
