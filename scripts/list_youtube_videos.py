"""
Usage:

$ python manage.py runscript list_youtube_videos --script-args <channel_id>

Example:

$ python manage.py runscript list_youtube_videos --script-args \
    @arenadofuturoNT > sources/youtube/pt_@arenadofuturoNT.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @EstaEscritoNT > sources/youtube/pt_@EstaEscritoNT.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @BibliaFacil > sources/youtube/pt_@BibliaFacil.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @ConsultoriodeFamilia > sources/youtube/pt_@ConsultoriodeFamilia.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @NTEvidencias > sources/youtube/pt_@NTEvidencias.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @novotempo > sources/youtube/pt_@novotempo.urls

$ python manage.py runscript list_youtube_videos --script-args \
    c/EscolaBíblicaNT > sources/youtube/pt_EscolaBíblicaNT.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @lugardepaztv > sources/youtube/pt_@lugardepaztv.urls

$ python manage.py runscript list_youtube_videos --script-args \
    c/FéparaHoje > sources/youtube/pt_FéparaHoje.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @OrigensNT > sources/youtube/pt_@OrigensNT.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @ReavivadosporSuaPalavraNT > sources/youtube/pt_@ReavivadosporSuaPalavraNT.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @NT180graus > sources/youtube/pt_@NT180graus.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @RevistaNT > sources/youtube/pt_@RevistaNT.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @adventistasbrasil > sources/youtube/pt_@adventistasbrasil.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @DraRosanaAlves > sources/youtube/pt_@DraRosanaAlves.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @SaldoExtra > sources/youtube/pt_@SaldoExtra.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @Hiperlinkados > sources/youtube/pt_@Hiperlinkados.urls

$ python manage.py runscript list_youtube_videos --script-args \
    c/AlémdosFatos > sources/youtube/pt_AlémdosFatos.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @novotemporadio > sources/youtube/pt_@novotemporadio.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @igrejaunaspsplive streams > sources/youtube/pt_@igrejaunaspsplive.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @igrejaunasp videos > sources/youtube/pt_@igrejaunasp_videos.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @igrejaunasp streams > sources/youtube/pt_@igrejaunasp_stream.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @LicoesdaBiblia > sources/youtube/pt_@LicoesdaBiblia.urls

$ python manage.py runscript list_youtube_videos --script-args \
    c/CódigoAbertoNT > sources/youtube/pt_CódigoAbertoNT.urls

$ python manage.py runscript list_youtube_videos --script-args \
    @PastorBullonBR > sources/youtube/pt_@PastorBullonBR.urls
"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_filtered_thumbnail_urls(channel_url, path="videos"):

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode

    driver = webdriver.Chrome(service=service, options=options)

    driver.get(channel_url + "/" + path)
    time.sleep(5)  # Wait for the JavaScript to load the content

    # Scroll down to load more videos
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);"
        )
        time.sleep(5)
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        if new_height == last_height:
            break
        last_height = new_height

    # Extract video URLs from thumbnail links within the specified div
    content_div = driver.find_element(
        By.XPATH,
        '//div[@id="contents" and contains(@class, "style-scope ytd-rich-grid-renderer")]',
    )
    thumbnail_elements = content_div.find_elements(
        By.XPATH,
        './/a[@id="thumbnail" and contains(@class, "yt-simple-endpoint inline-block style-scope ytd-thumbnail")]',
    )
    thumbnail_urls = [
        element.get_attribute("href")
        for element in thumbnail_elements
        if element.get_attribute("href")
    ]

    driver.quit()
    return thumbnail_urls


def run(*args):

    # Replace with the URL of the YouTube channel
    channel_url = "https://www.youtube.com/" + args[0]
    path = args[1] if len(args) > 1 else "videos"

    thumbnail_urls = get_filtered_thumbnail_urls(channel_url, path)
    for url in thumbnail_urls:
        print(url)
