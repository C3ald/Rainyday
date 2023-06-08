import requests
import itertools
from queue import Queue


def tamper_payload(payload):
    tampered_payloads = []

    # Original payload
    tampered_payloads.append(payload)
    tampered_payloads.append('`' + payload)
    tampered_payloads.append('`' + payload + '`')
    tampered_payloads.append("`" + payload + "'--")

    # Comment-based payload
    tampered_payloads.append(payload + " --")

    # Double quotation scheme
    tampered_payloads.append('"' + payload + '"')
    tampered_payloads.append('"' + payload + '--')
    tampered_payloads.append('"' + payload + '"--')

    # Single quotation scheme
    tampered_payloads.append("'" + payload + "'")
    tampered_payloads.append("'" + payload + "--")
    tampered_payloads.append("'" + payload + "'--")


def parse_request_file(file_path):
    headers = {}
    cookies = {}
    body = ""

    with open(file_path, "r") as file:
        lines = file.read().splitlines()

        # Extract headers, cookies, and body from the request file
        for line in lines[2:]:
            if line.strip():
                if ":" in line:
                    header_name, header_value = line.split(":", 1)
                    headers[header_name.strip()] = header_value.strip()
                else:
                    body += line.strip()

    return headers, cookies, body


class SQLi:
        def __init__(self, url, headers, params):
                self.url = url
                self.headers = headers
                self.params = params
        
        def gen_payloads(self, payload_file):
                