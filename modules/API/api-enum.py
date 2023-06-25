import requests
import itertools
import random
import queue
from concurrent.futures import ThreadPoolExecutor
import asyncio


def enum(base_url, cookie=None):
    routes = ['/api/v4']
    try:
        endpoints = open('./Rainyday/wordlists/routes.txt', 'r').readlines()
    except:
        endpoints = open('./wordlists/routes.txt', 'r').readlines()
    table = str.maketrans("", "", "(){}./,*&^%$#@!~`'= \n")

    endpoints = ['/' + s.translate(table) for s in endpoints]
    endpoints_2 = [
        '/users', '/posts', '/channels', '/user', '/post', '/channel', '/auth', '/logs', '/tokens', '/token', '/admin',
        '/administrator', '/users'
    ]
    combos = itertools.product(routes, endpoints, endpoints_2)
    combos_ = itertools.product(routes, endpoints_2, endpoints)
    combos_2 = itertools.product(routes, endpoints_2, endpoints)
    combos_3 = itertools.product(routes, endpoints)
    final_routes = []
    for combo in combos_:
        final_routes.append(''.join(combo))
    for combo in combos:
        final_routes.append(''.join(combo))

    for combo in combos_2:
        final_routes.append(''.join(combo))
    for combo in combos_3:
        final_routes.append(''.join(combo))
    final_routes = list(set(final_routes))

    que = queue.Queue()
    for item in final_routes:
        que.put(item)
    initial_length = que.qsize()

    async def get_url(url, cookie=None):
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0)', 'Accept': 'application/json',
                                             'Cookie': cookie})
            if res.status_code != 404 and (res.status_code != 302 and res.status_code < 500) and (
                    ' This page does not exist.' not in res.text or 'not found' not in res.text or 'Error' not in res.text):
                print(f"\nfound {url} with code: {res.status_code}\n")
            else:
                None
        except Exception as e:
            print(e)
            exit()

    while not que.empty():
        url = f'{base_url}{que.get()}'
        length = que.qsize()
        progress = round((initial_length - length) / initial_length * 100, 2)
        print(f'Progress: {progress}%   done {url}         ', end='\r')
        asyncio.run(get_url(url, cookie))
        asyncio.sleep(0)



if __name__ == '__main__':
        enum('http://jobs.amzcorp.local', cookie="session=.eJwtjtFqBCEMRf_F51I0Go371P2SQWNCh-7sgLpPpf9eB_blQg6c3PtrNu0yvs1t9pd8mG1v5mYycFa1rVUXE1WJjQCEC9uQMVCxUVtRzymrS0hCIi1BhoBIFapXyKQVPViuXCJJZlXAXLMPXG3E6hhj8K1JTg2zQAVCFUfesxMwa8hrSH-vQVqAR9dtnj_yXAghpOahkpUYiFPyJI4b2fW3AEafuDq1dnlylP2xlCljfl3xyeexeD8fsvC9HftzH7OXefax-NX7LIe8les0f_-w4lh2.ZJHcnQ.y4oQSiRKWBh4UGjNWjUEXYKM9wM;api_token=98d7f87065c5242ef5d3f6973720293ec58e434281e8195bef26354a6f0e931a1fd50a72ebfc8ead820cb38daca218d771d381259fd5d1a050b6620d1066022a")
