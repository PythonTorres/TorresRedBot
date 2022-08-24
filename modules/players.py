import requests
from bs4 import BeautifulSoup as BS

def Get_online(server_id):
    ans = requests.get('https://www.advance-rp.ru/join/#')
    page = BS(ans.content, 'html.parser')
    result = page.select('.gamers > span[itemprop="playersOnline"]')

    return result[server_id].text