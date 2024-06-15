"""
Transcribe audio files
"""

import torch

from decouple import config

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

MODEL_ID = "openai/whisper-large-v3"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
DEVICE = config("DEVICE", default="cuda")

device = torch.device(DEVICE)
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_ID, torch_dtype=TORCH_DTYPE, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(MODEL_ID)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    # max_new_tokens=128,
    # chunk_length_s=30,
    # batch_size=16,
    return_timestamps=True,
    torch_dtype=TORCH_DTYPE,
    device=device,
)


def transcribe(audio_file, opts, lang):
    """
    Transcribe audio file
    """

    result = pipe(
        audio_file, generate_kwargs={"task": "transcribe", "language": f"<|{lang}|>"}
    )

    return {
        "url": opts["webpage_url"],
        "title": opts["title"],
        "text": result["text"],
        "lang": lang,
    }
