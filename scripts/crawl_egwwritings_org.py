import os
import re
import json
from functools import lru_cache

from bs4 import BeautifulSoup

import requests

from crawler.models import Document

BASE_URL = "https://m.egwwritings.org"
INDEX_FILE = os.path.join("sources", "web", "egwwritings.org.jsonl")


class BookDownloader:
    """
    Download and save a book from the EGW Writings website
    """

    def __init__(self, book):
        self.book = book

    def save_book(self):
        """
        Download and save a book to the file system.
        """
        content = self.fetch_book_content()

        Document.objects.get_or_create(
            url=self.book["Url"],
            title=self.book["Title"],
            text=content,
            lang=self.book["Language"],
            document_type="book",
            author_id=self.book.get("Author"),
            text_revised=content,
            is_review_finished=True,
        )

        print(json.dumps(self.book, indent=2))

    def fetch_book_content(self):
        """
        Fetch the book content, going from page to page.
        """
        url = self.book["Url"]
        content = ""

        while url:
            page, url = self.parse_page_content(url)
            content += page
            print(".", end="", flush=True)

        return content

    def parse_page_content(self, url):
        """
        Download and parse a single page
        """
        n_max_attempts = 1000
        for attempt in range(1, n_max_attempts):
            try:
                page = requests.get(url, timeout=120)
                break
            except requests.exceptions.ReadTimeout as err:
                print(str(err), f"new attempt: {attempt}")
                continue

        page_content = page.content.decode()

        # Replacing <br> with newline
        page_content = re.sub(r"<br />", "\n", page_content)

        # HTML parser
        soup = BeautifulSoup(page_content, "html.parser")

        # Page content
        content = ""

        for item in soup.findAll("span", {"class": ["egw_content"]}):
            content += item.text + (os.linesep * 2)

        # Next page
        new_button = soup.find("a", {"class": "btn-large"}, string="Next")

        if not new_button or new_button.attrs["href"] == "#":
            return (content, None)

        next_url = BASE_URL + new_button.attrs["href"]

        return content, next_url


@lru_cache
def load_indexes(fname=INDEX_FILE):
    """
    Load the index file.
    """
    with open(fname, "r", encoding="utf8") as fin:
        return [json.loads(line) for line in fin.readlines()]


def dump_books(lang="pt"):
    """
    Download all books from the EGW Writings website.
    """
    books = [book for book in load_indexes() if book["Language"] == lang]

    for book in books:
        BookDownloader(book).save_book()


def create_index(start=1, max_book_id=30000, lang="pt"):
    """
    Create the index file for the EGW Writings website.
    """

    if start > 1:
        mode = "a"
    else:
        mode = "w"

    with open(INDEX_FILE, mode, encoding="utf8") as fout:

        for book in range(start, max_book_id + 1):

            details = get_book_info(book, lang)

            if not details:
                continue

            # Fix breadcrumb for other languages
            if details["Language"] != "en":
                details = get_book_info(book, details["Language"])

            print(f"{book}\t{details['Language']}\t{details['Title']}")
            fout.write(json.dumps(details) + os.linesep)
            fout.flush()


def get_book_info(book, lang, max_attempts=100):
    """
    Get the book information from the EGW Writings website.
    """
    url = book_url(book, lang)

    for attempt in range(1, max_attempts):
        try:
            page = requests.get(f"{url}/info", timeout=120)
            break
        except requests.exceptions.ReadTimeout as err:
            print(str(err), f"new attempt: {attempt}")
            continue

    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.content.decode(), "html.parser")

    return _parse_book_details(book, url, soup)


def _parse_book_details(pk, url, soup):
    book_title = soup.find("h1").text
    details = soup.find(attrs={"class": "book-details"})

    # Parsing breadcrumb
    breadcrumbs = []
    for li in soup.find("ul", attrs={"class": "breadcrumb"}).find_all("li"):
        if "class" in li.attrs and "dropdown" in li.attrs["class"]:
            breadcrumbs.append(li.find("a").text)
            break
        breadcrumbs.append(li.text)

    titles = [element.text for element in details.find_all("dt")]
    descriptions = [element.text for element in details.find_all("dd")]

    book_details = {
        detail: description for detail, description in zip(titles, descriptions)
    }
    book_details["Title"] = book_title
    book_details["Url"] = url
    book_details["Category"] = " > ".join(
        breadcrumbs[1:-1]
    )  # remove "home" and book name
    book_details["Id"] = pk

    return book_details


def book_url(book, lang):
    """
    Get the URL for the book in the EGW Writings website.
    """
    return f"{BASE_URL}/{lang}/book/{book}"


def run():
    """
    Run the script.
    """
    if not os.path.exists(INDEX_FILE):
        create_index()

    dump_books()
