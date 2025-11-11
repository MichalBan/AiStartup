from pathlib import Path
import random
import string
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import os
from markdown_pdf import MarkdownPdf, Section
import base64
import pdfkit
from datetime import datetime

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


def get_model_response_markdown(offer_text):
    system_prompt = "As output only generate the cv formatted in Markdown"
    return get_model_response(offer_text, system_prompt)


def get_model_response_text(offer_text):
    system_prompt = "As output only generate the cv text."
    return get_model_response(offer_text, system_prompt)

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


def generate_image(document_text):
    print("requesting image generation")
    response = client.responses.create(
        model="gpt-5",
        input=f"Generate an image of cv with following text:\n{document_text}",
        tools=[{"type": "image_generation"}],
    )
    image_data = [
        output.result
        for output in response.output
            if output.type == "image_generation_call"
    ]
    if image_data:
        print("saving image to file")
        image_base64 = image_data[0]
        with open("output/generated_image.png", "wb") as f:
            f.write(base64.b64decode(image_base64))
    else:
        print("image generation failed")


def save_as_pdf(markdown_text):
    print("saving document as pdf")
    pdf = MarkdownPdf()
    pdf.add_section(Section(markdown_text))
    pdf.save("output/from_markdown.pdf")
    print("document saved as pdf")


if __name__ == "__main__":
    target_url = 'https://justjoin.it'
    load_document()

    text = scraper(target_url)
    links = get_links_manually(text)
    link_text = scraper(target_url + random.choice(links))
    description = get_description(link_text)

    try:
        print('creating directory "output"')
        os.mkdir("output")
    except:
        print("directory already exists")

    #response = get_model_response_markdown(description)
    #save_as_pdf(response)

    # response = get_model_response_text(description)
    # generate_image(response)

    response = get_model_response_html(description)
    now = datetime.now()
    date_time = now.strftime("_%m-%d-%Y_%H-%M-%S")
    path = "output/from_html" + date_time + ".pdf"
    print(path)
    pdfkit.from_string(response, path)







   
       

