import os

from glob import glob

import torch

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from yt_dlp import YoutubeDL

import pandas as pd

from crawler.models import Document


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
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "outtmpl": f".download/{info_dict['id']}.wav",
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

        audio_file = ydl.prepare_filename(info_dict)
        return audio_file, info_dict


def transcribe(audio_file, opts):
    """
    Transcribe audio file
    """
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device,
    )

    result = pipe(
        audio_file, generate_kwargs={"task": "transcribe", "language": "<|pt|>"}
    )

    return {
        "url": opts["webpage_url"],
        "title": opts["title"],
        "text": result["text"],
        "lang": opts["language"],
    }


def run():
    """
    Crawl youtube videos from sources/youtube/*.urls
    """
    rows = []
    for fname in glob("sources/youtube/*.urls"):
        with open(fname, encoding="utf8") as file:
            urls = [line.strip() for line in file.readlines()]
            for url in urls:

                if Document.objects.filter(url=url).exists():
                    continue

                faudio, opts = download_youtube_audio(url)
                row = transcribe(faudio, opts)
                rows.append(row)

                # Save intermediate results
                df = pd.DataFrame(rows)
                fname_out = f"data/{opts['language']}/youtube/{opts['uploader_id']}/data.parquet"

                # ensure directory exists
                os.makedirs(os.path.dirname(fname_out), exist_ok=True)

                Document.objects.create(
                    url=row["url"],
                    title=row["title"],
                    text=row["text"],
                    lang=row["lang"],
                    document_type="youtube",
                    author_id=opts["uploader_id"],
                )

                df.to_parquet(fname_out)
