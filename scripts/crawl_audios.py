"""
Crawl audios from sources/audios/*.tsv
"""

import os
import hashlib

from glob import glob
from deepmultilingualpunctuation import PunctuationModel

import pandas as pd
import requests
import ffmpeg

from crawler.models import Document
from crawler.transcribe import transcribe

punct = PunctuationModel("kredor/punctuate-all")


def download_audio(audio_url):
    """
    Download audio from youtube video
    """
    # Download audio from youtube video
    response = requests.get(audio_url, timeout=60)
    audio_hash = hashlib.md5(audio_url.encode()).hexdigest()

    # extract audio extension from url
    ext = audio_url.split(".")[-1]

    fname = f".download/audio/{audio_hash}.{ext}"

    # ensure directory exists
    os.makedirs(os.path.dirname(fname), exist_ok=True)

    with open(fname, "wb") as file:
        file.write(response.content)

    # convert audio to flac, using sampling rate of 16kHz, mono channel
    fname_out = f".download/audio/{audio_hash}.flac"
    ffmpeg.input(fname).output(fname_out, ar=16000, ac=1).run(overwrite_output=True)

    # remove original audio file
    os.remove(fname)

    return fname_out


def process_audio(url, author, title, lang):
    """
    Process audio file
    """
    if Document.objects.filter(url=url).exists():
        return

    opts = {
        "webpage_url": url,
        "title": title,
    }

    faudio = download_audio(url)
    row = transcribe(faudio, opts, lang)

    # restore punctuation
    punct_restored = punct.restore_punctuation(row["text"])

    Document.objects.create(
        url=row["url"],
        title=title,
        text=row["text"],
        lang=lang,
        document_type="audio",
        author_id=author,
        text_revised=punct_restored,
        is_review_finished=False,  # needs human validation
    )

    return row


def run():
    """
    Crawl audios from sources/audios/*.tsv
    """
    rows = []
    for fname in glob("sources/audios/*.tsv"):
        lang, author_id = os.path.basename(fname).split("_")
        author_id = author_id.split(".")[0]

        with open(fname, encoding="utf8") as file:
            data = [line.strip().split("\t") for line in file.readlines()]
            for url, author, title in data:

                fname_out = f"data/{lang}/audios/{author_id}/data.parquet"

                # ensure directory exists
                os.makedirs(os.path.dirname(fname_out), exist_ok=True)

                row = process_audio(url, author, title, lang)
                rows.append(row)

                # Save intermediate results
                df = pd.DataFrame(rows)
                df.to_parquet(fname_out)
