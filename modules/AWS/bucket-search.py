from googlesearch import search
import requests, re
import json
from queue import Queue
import sys
import time as ti
from bs4 import BeautifulSoup

user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
headers = {'User-Agent': user_agent,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}



def google_dork(query, ses):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) saNDKSANClNASCLNDNAJSNLDNdnasldNSL '
#     }

    url = f"https://www.google.com/search?client=firefox-b-1-d&q={query}&start=5&num=3"
    
    r = ses.get(url, headers=headers)
    results = []
    print(r.content)

    soup = BeautifulSoup( r.content, 'html.parser' )
    h3tags = soup.find_all( 'h3', class_='r' )
    for h3 in h3tags:
            try:
            	data = re.search('url\?q=(.+?)\&sa', h3.a['href'])
            	print(data)
            	results.append(data)
            except Exception as e:
                    print(e)
            
    return results
        
def search_aws_buckets(domain):
    results = []
    query = f'site:{domain} inurl:s3.amazonaws.com'
    for url in search(query, num=1, pause=10):
        results.append(url)
    return results

def check_bucket_access(bucket_url):
    response = requests.head(bucket_url, headers=headers)
    try:
    	if response.status_code == 200:
        	print(f"\nOpen bucket found: {bucket_url}", end='\n')
    	else:
        	print(f"\nClosed bucket on: {bucket_url}", end='\n')
    except:
            print(f"\nClosed bucket on: {bucket_url}", end='\n')


if __name__ == '__main__':
        print('first argument is list of subdomains')
        targets = open(sys.argv[1], 'r')
        domains = Queue()
        of = 0
        for target in targets.readlines():
                of = of +1
                t = target.strip()
                if 'http://' in t:
                	t  = t.strip('http://')
                if 'https://' in t:
                        t = t.strip('https://')
                #print(f"putting: {of}        / {len(targets.readlines())}                 ", end='\r')
                
                # if '.com' in t:
                #         t = t.strip('.com')
                domains.put(t)
        found = []
        print('scanning now!!!')
        ses = requests.Session()
        while domains.empty() == False:
                domain = domains.get()
                print(f'scanning: {domain}                               ',end='\r')
                ti.sleep(1)
                #query = f'site:{domain} inurl:s3.amazonaws.com'
                #bucket_urls = google_dork(query, ses)
                bucket_urls = search_aws_buckets(domain)
                
                if bucket_urls != None:
                	if len(bucket_urls) > 0:
                        	for url in bucket_urls:
                                	if url not in found:
                                		check_bucket_access(url)
                                		found.append(url)



# bucket_urls = search_aws_buckets(search_domain)

#     if len(bucket_urls) > 0:
#         print(f"Found {len(bucket_urls)} AWS buckets for {search_domain}:")
#         for url in bucket_urls:
#             check_bucket_access(url)
#     else:
#         print(f"No AWS buckets found for {search_domain}")

        
        