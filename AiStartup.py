import requests
from bs4 import BeautifulSoup
import re

def scraper(url):
    # request the target website
    response = requests.get(url)

    # verify the response status
    if response.status_code != 200:
        return f"status failed with {response.status_code}"
    else:
        return response.text

        
if __name__ == "__main__":
    target_url = "https://justjoin.it/"
    text = scraper(target_url)

    position_names = []
    for m in re.finditer('alt=', text):
        name_start = m.end() + 1
        name_end = name_start
        while text[name_end] != "\"":
            name_end = name_end + 1
        position_names.append(text[name_start:name_end])
    

    for name in position_names:
        print(name)
       

