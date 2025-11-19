from pathlib import Path
import random
import string
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import os
from datetime import datetime
from OutputSaving import create_shortcut, save_html_as_pdf
import urllib.parse

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

def load_document():
    global file

    print("loading document")
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

    file = client.files.create(
        file=open(doc_name, "rb"),
        purpose="assistants"
    )
    print("loading document done")


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


# def get_model_response_markdown(offer_text):
#     system_prompt = "As output only generate the cv formatted in Markdown"
#     return get_model_response(offer_text, system_prompt)


# def get_model_response_text(offer_text):
#     system_prompt = "As output only generate the cv text."
#     return get_model_response(offer_text, system_prompt)


def get_model_response_html(offer_text):
    system_prompt = "As output only generate the cv formatted in HTML."
    return get_model_response(offer_text, system_prompt)


def get_model_response(offer_text, system_prompt):
    prompt =f"Modify the cv to make it more suitable for the job offer:\n\n{offer_text}"
    print(f"using OpenAI API with system prompt:\n{system_prompt}\nand user prompt:\n{prompt}\nwaiting for response")
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": system_prompt
            },
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
        ],
    )
    print("model responded")
    return response.output_text

def try_make_dir(path):
    try:
        print(f'creating directory {path}')
        os.mkdir(path)
    except:
        print(f'directory {path} already exists')


if __name__ == "__main__":
    target_url = 'https://justjoin.it'
    load_document()

    text = scraper(target_url)
    links = get_links_manually(text)

    path = "output"
    try_make_dir(path)
    path = path + "/" + datetime.now().strftime("_%m-%d-%Y_%H-%M-%S")
    try_make_dir(path)

    for i in range(2):
        offer_url = target_url + links[1]
        link_text = scraper(offer_url)
        description = get_description(link_text)
        response = get_model_response_html(description)

        loop_path = path + "/" + str(i+1)
        try_make_dir(loop_path)
        save_html_as_pdf(loop_path + "/CV.pdf", response)
        create_shortcut(loop_path + "/shortcut.url", offer_url)

