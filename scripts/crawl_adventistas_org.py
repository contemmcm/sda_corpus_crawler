"""
Iterates over all pages in https://noticias.adventistas.org/pt/
Usage:

$ python manage.py runscript crawl_adventistas_org
"""

import requests

from bs4 import BeautifulSoup

from crawler.models import Document


def parse_text(item):
    soup = BeautifulSoup(item["content"]["rendered"], "html.parser")

    text = ""

    for p in soup.find_all("p"):
        text += p.get_text() + "\n\n"

    return text


def run():
    """
    Crawl noticias.adventistas.org
    """
    page = 1

    Document.objects.filter(url__contains="noticias.adventistas.org").delete()

    while True:
        url = f"https://noticias.adventistas.org/pt/wp-json/wp/v2/posts?&page={page}"
        response = requests.get(url, timeout=60)

        if response.status_code != 200:
            break

        data = response.json()

        for item in data:

            text = parse_text(item)

            if isinstance(item["acf"], bool):
                author = None
            elif "custom_author" in item["acf"] and item["acf"]["custom_author"] != "":
                author = item["acf"]["custom_author"]
            elif "author" in item:
                author = f"author_{item['author']}"
            else:
                author = None

            obj = Document.objects.create(
                url=item["link"],
                title=item["title"]["rendered"],
                text=text,
                lang="pt",
                document_type="news",
                author_id=author,
                text_revised=text,
            )

            print(obj.title)

        page += 1
