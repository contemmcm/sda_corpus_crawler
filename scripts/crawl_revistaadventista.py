"""
Usage:

$ python manage.py runscript crawl_revistaadventista
"""

import json
import requests

from bs4 import BeautifulSoup

from crawler.models import Document

INDEX_FILE = "sources/web/revistaadventista.com.br.jsonl"


def run():
    """
    Crawl revistaadventista.com.br
    """
    rows = load_indexes_urls()

    for row in rows:
        download(row)


def download(entry):
    """
    Download the content of the entry
    """

    response = requests.get(entry["url"], timeout=60)

    if response.status_code != 200:
        return False

    soup = BeautifulSoup(response.content, "html.parser")

    article = soup.find("article")

    p_list = article.find_all("p")

    text = "\n\n".join([entry["subtitle"]] + [p.text for p in p_list])

    Document.objects.get_or_create(
        url=entry["url"],
        title=entry["title"],
        text=text,
        lang="pt",
        document_type="news",
        author_id="Revista Adventista",
        text_revised=text,
        is_review_finished=True,
    )

    return True


def load_indexes_urls():
    """
    Load the index file and return the rows
    """
    rows = []
    with open(INDEX_FILE, encoding="utf8") as f:
        for line in f:
            data = json.loads(line)
            rows.append(data)
    return rows
