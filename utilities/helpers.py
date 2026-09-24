import beautifulsoup
import requests
import sys

from lxml import etree
from io import BytesIO
from urllib.parse import urljoin

def get_params(content: bytes) -> dict[str, str | None]:
    params: dict[str, str | None] = {}
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)

    for input_elem in tree.findall('.//input'):
        name = input_elem.get('name')
        if name is not None:
            params[name] = input_elem.get('value', None)

    return params

def get_form_fields(content: bytes) -> list:
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

def search_tree(content: bytes, term: str) -> bool:
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)
    return bool(tree.xpath(f".//*[contains(normalize-space(string(.)), '{term}')]"))

def get_element_content(content: bytes, term: str) -> str:
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)
    tree.xpath(f".//*[contains(normalize-space(string(.)), '{term}')]")

def login(target: str, path: str, username_input: str, password_input: str, username: str, password: str, error_msg, timeout=10) -> requests.Session:
    session = requests.Session()

    try:
        response = session.get(urljoin(target, path), timeout=timeout)
    except requests.RequestException as e:
        print(f'An error occurred: {e}')
        sys.exit()

    login_form = get_form_fields(response.content)[0]
    login_data = {}

    for control in login_form['controls']:
        login_data[control['name']] = control['value']

    login_data[username_input] = username
    login_data[password_input] = password

    try:
        login_response = session.post(urljoin(target, login_form['action']), login_data, timeout=timeout)
    except requests.RequestException as e:
        print(f'An error occurred: {e}')
        sys.exit()

    if login_response.status_code != requests.codes.ok or search_tree(login_response.content, error_msg):
        print(f'Login attempt failed with status code {login_response.status_code}')
        sys.exit()

    print('Login was successful')
    return session