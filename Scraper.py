import requests
from bs4 import BeautifulSoup

data = requests.get('https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/ransomware.html')

soup = BeautifulSoup(data.text, 'html.parser')

for tr in soup.find_all('tr'):
    for td in tr.find_all('td'):
        print(td.text)
