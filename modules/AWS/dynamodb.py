import boto3
import csv


class DynamoDB:
        def __init__(self, access_key, private_access_key, region_name, endpoint_url):
                # self.access_key = access_key
                # self.private_key = private_access_key
                self.dynamo = boto3.resource('dynamodb', region_name=region_name, endpoint_url=endpoint_url, aws_access_key_id=access_key, aws_secret_access_key=private_access_key)
        
        def dump_tables(self):
                tables = list(self.dynamo.tables.all())
                for table in tables:
                        print(f"found table: {table}")
                return tables
        
        
        def dump_items(self, table_name, path_for_dump):
                items = self.dynamo.Table(table_name).scan()
                if path_for_dump[-1] == c:
                        path_for_dump = path_for_dump[:-1]
                filed = open(f'{path_to_save}/{table_name}.csv', 'w')
                writer = csv.writer(filed)
                header = True
                for item in items['Items']:
                        if header:
                                writer.writerow(item.keys())
                                header = False
                                writer.writerow(item.values())
                print(f"dumped to {path_for_dump}")
                return 1
