"""
You need to export your YouTube cookies from your web browser. This can be done using a 
browser extension like EditThisCookie (Chrome) or Cookies.txt (Firefox).

Chrome (EditThisCookie)

1. Install the EditThisCookie extension.
2. Go to youtube.com.
3. Click on the extension icon and select "Export" to save your cookies as a .json file.


Usage:

$ python manage.py runscript crawl_youtube --script-args *.urls cookies.json
"""

import os

from glob import glob
from deepmultilingualpunctuation import PunctuationModel

from yt_dlp import YoutubeDL, DownloadError

import pandas as pd

from crawler.models import Document
from crawler.transcribe import transcribe

punct = PunctuationModel("kredor/punctuate-all")


def download_youtube_audio(youtube_url, cookies):
    """
    Download audio from youtube video
    """

    if cookies and not os.path.exists(cookies):
        cookies = None

    info_dict = YoutubeDL({"cookies": cookies}).extract_info(
        youtube_url, download=False
    )

    ydl_opts = {
        "cookies": cookies,
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "flac",
                "preferredquality": "192",
            }
        ],
        "outtmpl": f".download/youtube/{info_dict['id']}.%(ext)s",
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
        audio_file = f".download/youtube/{info_dict['id']}.flac"
        return audio_file, info_dict


def run(*args):
    """
    Crawl youtube videos from sources/youtube/*.urls
    """
    source = args[0] if args else "*.urls"
    cookies = args[1] if len(args) > 1 else None

    rows = []
    for fname in glob(f"sources/youtube/{source}"):
        lang = os.path.basename(fname).split("_")[0]
        with open(fname, encoding="utf8") as file:
            urls = [line.strip() for line in file.readlines()]
            for url in urls:

                if Document.objects.filter(url=url).exists():
                    continue

                is_downloaded = False

                for _ in range(3):
                    try:
                        faudio, opts = download_youtube_audio(url, cookies)
                        is_downloaded = True
                        break
                    except DownloadError:
                        continue

                if not is_downloaded:
                    continue  # skip this video

                row = transcribe(faudio, opts, lang)

                # restore punctuation
                try:
                    punct_restored = punct.restore_punctuation(row["text"])
                except AssertionError as err:
                    print(f"Error: {err}")
                    continue
                except IndexError as err:
                    print(f"Error: {err}")
                    continue

                rows.append(row)

                # Save intermediate results
                df = pd.DataFrame(rows)

                fname_out = f"data/{lang}/youtube/{opts['uploader_id']}/data.parquet"

                # ensure directory exists
                os.makedirs(os.path.dirname(fname_out), exist_ok=True)

                Document.objects.create(
                    url=row["url"],
                    title=row["title"],
                    text=row["text"],
                    lang=lang,
                    document_type="youtube",
                    author_id=opts["uploader_id"],
                    text_revised=punct_restored,
                    is_review_finished=False,  # needs human validation
                )

                df.to_parquet(fname_out)

                # remove audio file
                os.remove(faudio)
