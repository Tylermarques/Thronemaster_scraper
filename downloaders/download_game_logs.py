from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing.dummy import Pool as ThreadPool
import time
import os

def downloader(game_log_id):
    if game_log_id % 100 == 0:
        print(f'Downloading review {game_log_id} ... ', end='')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    url = f'http://game.thronemaster.net/?game={game_log_id}&review=1'
    browser = webdriver.Chrome(chrome_options=chrome_options)
    try:
        file_name = 'start_moves/' + str(url[url.find('game=')+5:].split('&')[0])
        browser.get(url)
        innerHTML = browser.execute_script("return document.body.innerHTML")
        with open(file_name, 'wb') as file:
            file.write(innerHTML.encode('utf-8'))
        browser.close()
        return innerHTML
    except Exception as e:
        print('FAILED')
        browser.close()
        print(e)
    time.sleep(0.33)
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