import string
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
client = OpenAI()

def scraper(url):
    # request the target website
    response = requests.get(url)

    # verify the response status
    if response.status_code != 200:
        print(f"status failed with {response.status_code}")
        exit()
        return ""
    else:
        return response.text

def get_links_manually(text: string):
    links = []
    link_start = text.find('href="/job-offer/')
    while link_start >= 0:
        link_start = link_start + 6
        link_end = link_start
        while text[link_end] != '"':
            link_end = link_end + 1
        links.append(text[link_start:link_end])
        link_start = text.find('href="/job-offer/', link_end)
    return links

def get_links_AI(text):
    print(f"length of website: {len(text)}")
    response = client.responses.create(
        model="gpt-5-nano",
        input="Create a comma separated list of links to job offers from the following website:\n" + text
    )
    return response.output_text.split(',')

        
if __name__ == "__main__":
    target_url = 'https://justjoin.it'
    text = scraper(target_url)
    links = get_links_manually(text)

    for link in links:
        print(target_url + link)



   
       

