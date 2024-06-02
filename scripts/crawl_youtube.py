import os

from glob import glob
from deepmultilingualpunctuation import PunctuationModel

from yt_dlp import YoutubeDL

import pandas as pd

from crawler.models import Document
from crawler.transcribe import transcribe

punct = PunctuationModel("kredor/punctuate-all")


def download_youtube_audio(youtube_url):
    """
    Download audio from youtube video
    """

    info_dict = YoutubeDL().extract_info(youtube_url, download=False)

    ydl_opts = {
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


def run():
    """
    Crawl youtube videos from sources/youtube/*.urls
    """
    rows = []
    for fname in glob("sources/youtube/*.urls"):
        lang = os.path.basename(fname).split("_")[0]
        with open(fname, encoding="utf8") as file:
            urls = [line.strip() for line in file.readlines()]
            for url in urls:

                if Document.objects.filter(url=url).exists():
                    continue

                faudio, opts = download_youtube_audio(url)
                row = transcribe(faudio, opts, lang)

                # restore punctuation
                punct_restored = punct.restore_punctuation(row["text"])

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
