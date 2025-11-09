import string
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import os

client = OpenAI()

def scraper(url):
    print(f"scrapping url:{url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"status failed with {response.status_code}")
        return ""
    else:
        print("scrapping done")
        return response.text

def get_links_manually(text: string):
    print("extracting links from website")
    links = []
    link_start = text.find('href="/job-offer/')
    while link_start >= 0:
        link_start = link_start + 6
        link_end = link_start
        while text[link_end] != '"':
            link_end = link_end + 1
        links.append(text[link_start:link_end])
        link_start = text.find('href="/job-offer/', link_end)
    print("extraction done")
    return links

def get_links_AI(text):
    response = client.responses.create(
        model="gpt-5-nano",
        input="Create a comma separated list of links to job offers from the following website:\n" + text
    )
    return response.output_text.split(',')

def load_document():
    global file
    print("loading document")
    doc_name = ""
    for f in os.listdir():
        if f.endswith('.pdf'):
            doc_name = f
    if doc_name == "":
        print("failed to load document")
        return

    file = client.files.create(
        file=open(doc_name, "rb"),
        purpose="user_data"
    )
    print("document done")

if __name__ == "__main__":
    target_url = 'https://justjoin.it'
    text = scraper(target_url)
    links = get_links_manually(text)

    load_document()
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "file_id": file.id,
                    },
                    {
                        "type": "input_text",
                        "text": f"Using provided cv give me a quick answer if this candidate id suitable for role of junior java developer",
                    },
                ]
            }
        ]
    )
    print(response.output_text)




   
       

