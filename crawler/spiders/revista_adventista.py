import re
from bs4 import BeautifulSoup
from scrapy import Spider


class RevistaAdventistaSpider(Spider):
    name = "Revista Adventista"
    start_urls = [
        "https://www.revistaadventista.com.br/categorias/destaques/",
        "https://www.revistaadventista.com.br/categorias/noticias/",
        "https://www.revistaadventista.com.br/categorias/artigos/",
        "https://www.revistaadventista.com.br/categorias/entrevista/",
        "https://www.revistaadventista.com.br/categorias/editorial/",
        "https://www.revistaadventista.com.br/categorias/estante/",
        "https://www.revistaadventista.com.br/categorias/bussola/",
        "https://www.revistaadventista.com.br/categorias/perfil/",
        "https://www.revistaadventista.com.br/categorias/podcast/",
        "https://www.revistaadventista.com.br/categorias/em-familia/",
        "https://www.revistaadventista.com.br/categorias/guia/",
        "https://www.revistaadventista.com.br/categorias/logos/",
        "https://www.revistaadventista.com.br/categorias/olhar-ra/",
        "https://www.revistaadventista.com.br/da-redacao/",
    ]

    def parse(self, response):

        soup = BeautifulSoup(response.body, "lxml")

        last_page = soup.find("a", class_="last")
        last_page_num = int(last_page["href"].split("/")[-2]) if last_page else 1

        current_page = response.url.split("/")[-2]
        current_page_num = int(current_page) if current_page.isdigit() else 1

        for element in soup.find_all("article"):
            title = element.find("h2").text.strip()
            subtitle = element.find("div", class_="entry").find("p").text.strip()
            url = element.find("a")["href"]

            yield {"title": title, "subtitle": subtitle, "url": url}

        if current_page_num < last_page_num:
            next_page_num = current_page_num + 1

            if current_page_num == 1:
                next_page_url = response.url + f"page/{next_page_num}/"
            else:
                next_page_url = re.sub(
                    r"page/\d+/", f"page/{next_page_num}/", response.url
                )

            yield response.follow(next_page_url, self.parse)
