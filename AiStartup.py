import random
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

    doc_name = ""
    for f in os.listdir():
        if f.endswith('.pdf'):
            doc_name = f
    if doc_name == "":
        print("document file doesn't exist")
        return

    files = client.files.list()
    for f in files:
        if f.filename == doc_name:
            file = f
            print("document already loaded")
            return

    print("loading document")
    file = client.files.create(
        file=open(doc_name, "rb"),
        purpose="user_data"
    )
    print("document done")

def condition(tag):
    if not tag.has_attr("class"):
        return False
    for class_name in tag.get("class"):
        if class_name.startswith("ql-header-") or re.search("[pP]aragraph", class_name):
            return True
    return False

def get_description(html_text):
    print(f'extracting description')
    soup = BeautifulSoup(html_text, "html.parser")
    bullet_lists = soup.findAll(condition)

    text = ""
    for bullet in bullet_lists:
        text = text + bullet.get_text() + "\n"
    print(f'extraction done, num letters: {len(text)}')
    return text


if __name__ == "__main__":
    target_url = 'https://justjoin.it'
    text = scraper(target_url)
    links = get_links_manually(text)
    link_text = scraper(target_url + random.choice(links))
    description = get_description(link_text)

    load_document()
    prompt =f"Using provided cv give me a quick answer if this candidate is suitable for the following job offer:\n\n{description}" 
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
                        "text": prompt,
                    },
                ]
            }
        ]
    )
    print(response.output_text)




   
       

