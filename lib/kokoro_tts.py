from kokoro import KPipeline
import soundfile as sf
import tempfile
import os
from lib.context import Context

# Initialize Kokoro pipeline
context = Context()

def generate_tts(text, lang_code, voice):
    pipeline = KPipeline(lang_code=lang_code)
    try:
        generator = pipeline(
            text, voice=voice,
            speed=1, split_pattern=r'\n+'
        )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            for _, _, audio in generator:
                sf.write(tmp_file.name, audio, 24000)
            return tmp_file.name
    except Exception as e:
        print(f"Error in Kokoro TTS: {e}")
        raise
