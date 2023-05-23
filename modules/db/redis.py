import redis
import os

class RedisDB:
        def __init__(self, host, port, password=None):
                self.host = host
                self.red = redis.Redis(host=host, port=port, password=password)
        
        def get_tables(self):
                tables = self.red.Keys()
                return tables
        
        def dump_table(self, table_name):
                data = self.red.dump(table_name)
                f = open(f'{table_name}.rdb', 'wb')
                f.write(data)
        
        def dump(self):
                tables = self.get_tables()
                for table in tables:
                        print(f'dumping table: {table.decode("utf-8")}')
                        self.dump_table(table.decode('utf-8'))
                