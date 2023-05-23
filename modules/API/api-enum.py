import requests, json
import itertools
import random
import queue
from concurrent.futures import ThreadPoolExecutor

def enum(base_url, threads):
        routes = ['/api/v1', '/api/v2', '/api/v3', '/api/v4', '/api/v5', '/api/v6']
        # routes = ['/api/v4']
        endpoints = open('./Rainyday/wordlists/routes.txt', 'r').readlines()
        table = str.maketrans("","", "(){}./,*&^%$#@!~`'= \n")
        
        endpoints = ['/'+ s.translate(table) for s in endpoints]
        endpoints_2 = ['/users', '/posts', '/channels', '/user', '/post', '/channel', '/auth', '/logs', '/tokens', '/token', '/admin']
        combos = itertools.product(routes, endpoints, endpoints_2)
        #combos_2 = itertools.product(routes, endpoints_2, endpoints)
        #combos_3 = itertools.product(routes, endpoints)
        #combos = combos + combos_2
        final_routes = []
        for combo in combos:
                final_routes.append(''.join(combo))
        
        que = queue.Queue()
        for item in final_routes:
                que.put(item)
        initial_length = que.qsize()
        # while que.empty() == False:
        #         url = f'{base_url}{que.get()}'
        #         length = que.qsize()
        #         progress = round((initial_length-length)/initial_length * 100, 2)
        #         print(f'Progress: {progress}%   done',end='\r')
        #         try:
        #                 res = requests.get(url)
        #                 if res.status_code != 404:
        #                         print(f"found {url} with code: {res.status_code}\n")
        #         except Exception as e:
        #                 None
        def get_url(url):
                try:
                        res = requests.get(url)
                        if res.status_code != 404:
                                print(f"\nfound {url} with code: {res.status_code}\n")
                except Exception as e:
                        print(e)
                        exit()
        with ThreadPoolExecutor(max_workers=threads) as executor:
                while not que.empty():
                        url = f'{base_url}{que.get()}'
                        length = que.qsize()
                        progress = round((initial_length-length)/initial_length * 100, 2)
                        print(f'Progress: {progress}%   done {url}         ',end='\r')
                        executor.submit(get_url,args=(url,))


if __name__ == '__main__':
        enum('http://jobs.amzcorp.local', 2)
