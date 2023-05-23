import grpc
import subprocess, os
from grpc_tools import protoc
import importlib

def grpc_enum_proto(grpc_url):
        """ grpc url should not be in http or https but should be IP:PORT"""
        os.system('rm -r ./proto')
        os.system('mkdir ./proto')
        get_services = os.system(f"grpcurl -plaintext {grpc_url} list > ./proto/services.txt")
        services = open('services.txt', 'r').readlines()
        for service in services:
                service = service.strip()
                data = os.system(f'grpcurl -plaintext {grpc_url} describe {service} >> ./proto/service.proto')
                os.system('echo "\n\n\n" >> ./proto/service.proto')
        #print('turn the service.proto file into python ex: python -m grpc_tools.protoc -I <proto_file_directory> --python_out=<output_directory> --grpc_python_out=<output_directory> <proto_file>')
        
        return 1


def generate_grpc_code():
        os.system('rm -r ./pyproto')
        os.system('mkdir pyproto')
        protoc.main(['grpc_tools.protoc',
        '--proto_path=./proto/',
        '--python_out=./pyproto/',
        '--grpc_python_out=./pyproto',
        './proto/service.proto'
    ])

if __name__ == '__main__':
        grpc_enum_proto('10.129.226.159:50051')
        generate_grpc_code()