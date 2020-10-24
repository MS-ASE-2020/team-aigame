import requests
import re
from tqdm import tqdm
import multiprocessing
from functools import reduce
import logging
from data.dataset import Game
import json


def get_lin(origin_url, linurl=True):
    '''
    To get each url of .lin file.
    :param linurl: Whether return url of .lin file, otherwise, return list of directly obtained urls.
    '''
    if origin_url[-4:] == '.lin':
        print(f"get {origin_url}")
        return [origin_url]
    try:
        response = requests.get(origin_url)
        if response.status_code != 200:
            print(origin_url + ' requests error\n')
            return []
    except:
        print(origin_url + ' requests error\n')
        return []
    text = response.text
    pattern = re.compile("<A HREF = \"(.*?)\">")
    urls = re.findall(pattern, text)
    linurlList = []
    for url in urls:
        if url[:3] not in ['htt', '../', '..\\']:
            if linurl:
                linurlList.extend(get_lin('/'.join(origin_url.split('/')[:-1]+[url])))
            else:
                linurlList.append('/'.join(origin_url.split('/')[:-1]+[url]))
    return linurlList


def deal_lin(url: str):
    '''
    To deal with each lin file and get the json of Game.
    :param url: url of lin
    :return: None
    '''
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(url + ' requests error\n')
            return []
    except:
        print(url + ' requests error\n')
        return []
    text = response.text
    lin_list = text.split('qx|')[1:]
    for num, lin in enumerate(lin_list):
        game = Game(url, lin)
        name='_'.join(url.split('/')[5:])+str(num)
        if game.valid:
            with open(f"G:/AIGame/data_1024/{name}.json", 'w') as f:
                json.dump(game, f, default=lambda obj: obj.__dict__)


def main():
    print("-----Start get url of '.lin' file from website-----")
    url_list = get_lin("http://www.sarantakos.com/bridge/vugraph.html", False)
    num_core = 4
    if num_core == 1:
        linurl_list = []
        for url in tqdm(url_list):
            # file_info_name = BlobLister.list_blobs(container)
            file_info = get_lin(url)
            linurl_list.extend(file_info)
    else:
        pool = multiprocessing.Pool(num_core)
        results = pool.starmap(get_lin, tqdm([[url] for url in url_list]))
        print('Finish the pool calculate\n')
        pool.close()
        pool.join()
        linurl_list = reduce(lambda x, y: x + y, results)
    print(f"Get {len(linurl_list)} '.lin' files")

    print("-----Start deal with .lin file-----")
    if num_core == 1:
        for linurl in tqdm(linurl_list):
            deal_lin(linurl)
    else:
        pool = multiprocessing.Pool(num_core)
        pool.starmap(deal_lin, tqdm([[url] for url in linurl_list]))
        print('Finish the pool calculate\n')
        pool.close()
        pool.join()


if __name__ == '__main__':
    main()
    # deal_lin("http://www.sarantakos.com/bridge/vugraph/1962/usita/pf2c.lin")
