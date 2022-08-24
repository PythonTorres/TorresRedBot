import requests
from bs4 import BeautifulSoup as BS
import ast

def Get_account_id(nickname):

    s = requests.Session()
    s.get('https://www.advance-rp.ru/')
    s.get('https://www.advance-rp.ru/donate/')

    serverName = 'red'
    server = str(serverName).lower()

    if server == 'red' or server == 'red server':
        server_id = 1
    elif server == 'green' or server == 'green server':
        server_id = 2
    elif server == 'blue' or server == 'blue server':
        server_id = 3
    elif server == 'lime' or server == 'lime server':
        server_id = 4    

    payload = {
        'g-recaptcha-response': '',
        'sum': 1,
        'account': nickname,
        'service': 'unitpay',
        'server': server_id
    }

    ans = s.post('https://www.advance-rp.ru/donate/request/do/', data = payload)
    print(ans.text)
    print(type(ans.text))
    result = ans.text.split(',')
    print(result)
    print(type(result))
    result.reverse()
    account_id_field = result[0]
    account_id_field = '{' + account_id_field
    account_id = eval(account_id_field)
    if account_id['id']:
        result = account_id['id']
    else:
        result = 'unknown'
    return result