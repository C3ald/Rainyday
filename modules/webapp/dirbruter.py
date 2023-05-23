import os, sys, time
import requests as r
from queue import Queue
from threading import Thread


class Dirbruter:
        def __init__(self, url, threads=25, wordlist='/usr/share/dirb/wordlists/big.txt'):
                self.url = url
                self.threads=threads
                self.wordlist = wordlist
                self.extensions = ['.php', '.txt', '.sh', 'aspx', 'asp', '.c', '.db', '.sqlite', '.rss', '.rc']
                self.agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_1_8) AppleWebKit/603.18 (KHTML, like Gecko) Chrome/55.0.2669.310 Safari/603'
        
        def get_words(self, resume=None):
                def extend_words(word):
                        if '.' in word:
                                words.put(f'/{word}')
                        else:
                                words.put(f'/{word}/')
                        for extension in self.extensions:
                                words.put(f'/word{extension}')
                with open(self.wordlist, errors='ignore') as f:
                        raw_words = f.read()
                found_resume=False
                words = Queue()
                for word in raw_words.split():
                        if resume is not None:
                                if found_resume:
                                        extend_words(word)
                        else:
                                extend_words(word)
                return words
        
        def brute(self, words):
                headers = {'User-Agent':self.agent}
                while not words.empty():
                        url = f'{self.url}{words.get()}'
                        try:
                                re = r.get(url, headers=headers)
                        except r.exceptions.ConnectionError:
                                None
                                continue
                        
                        if re.status_code ==200:
                                print(f'200 on url: {url}')
                        if re.status_code > 300 and 'Not found' not in re.text and re.status_code != 404:
                                print(f'{re.status_code} on url: {url}')
        def start(self):
                words = self.get_words()
                for _ in range(self.threads):
                        t = Thread(target=self.brute, args=(words,))
                        t.start()
                        time.sleep(0.1)

if __name__ == '__main__':
        url = sys.argv[1]
        dirb = Dirbruter(url)
        dirb.start()