import boto3
import os
import sys

class S3:
        def __init__(self, endpoint_url, access_key=None, private_key=None, region='us-east-2'):
                self.access_key = access_key
                self.private_key = private_key
                self.region = region
                self.s3 = None
                self.s3 = boto3.resource(service_name='s3',region_name=self.region,aws_access_key_id=self.access_key, aws_secret_access_key=self.private_key, endpoint_url=endpoint_url)

                
        
        def list_s3(self):
                i = 1
                buckets = []
                for bucket in self.s3.buckets.all():
                        print(f"found s3 bucket: {bucket.name}")
                        buckets.append(bucket.name)
                        i = i+1
                print(f'found a total of: {i} s3 buckets!')
        
        def list_content(self, bucket_name, p=False):
                objs = self.s3.Bucket(bucket_name).objects.all()
                if p == True:
                        for obj in objs:
                                print(obj)
                return objs
        
        def  dump_content(self, bucket_name, path_for_dump):
                c = '/'
                if path_for_dump[-1] == c:
                        path_for_dump = path_for_dump[:-1]
                objs = self.list_content(bucket_name)
                for obj in objs:
                        f = self.s3.Bucket(bucket_name).download_file(Key=obj, Filename=f'{path_for_dump}/{obj}')
                print("DONE!!!")
