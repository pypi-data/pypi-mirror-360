# %% =================================================
from google.genai import Client, types
from io import BytesIO
from pytubefix import Buffer, YouTube


def youtube_obj(url: str | None) -> YouTube | None:
    if not url:
        return None
    try:
        yt = YouTube(url)
        yt.check_availability()
        return yt
    except Exception:
        return None


# %% ================================================= caption


def add_punctuation(api_key: str, transcript: str) -> str:
    """Add punctuation to a transcript using Gemini's LLM."""
    sys_prompt = "add punctuation to the following text with proper paragraph, give the output without other comments"
    client = Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        config=types.GenerateContentConfig(system_instruction=sys_prompt),
        contents=transcript,
    )
    return response.text


# %% ================================================= transcribe


def download_yt_audio(yt: YouTube) -> tuple[Buffer, str]:
    """download the lowest quality audio stream to a pytubefix Buffer object"""
    audio_stream = (
        yt.streams.filter(only_audio=True, audio_codec="opus").order_by("abr").first()
    )
    buffer = Buffer()
    buffer.download_in_buffer(audio_stream)
    mime_type = audio_stream.mime_type
    return buffer, mime_type


def get_audio_part(mime_type: str, buffer: Buffer) -> types.Part:
    """convert the pytubefix Buffer object to a Gemini types.Part object"""
    return types.Part.from_bytes(data=buffer.read(), mime_type=mime_type)


def remove_duplicate_gemini_audio(name: str, client: Client):
    """adding audio with the same name to Gemini cloud storage will raise an error, so remove the existing one"""
    audio_files = [f.name for f in client.files.list()]
    for file_name in audio_files:
        if name in file_name:
            client.files.delete(name=file_name)


def upload_gemini_audio(
    name: str, buffer: Buffer, mime_type: str, client: Client
) -> types.File:
    """upload the audio to Gemini cloud storage"""
    io_obj: BytesIO = buffer.buffer
    io_obj.seek(0)
    upload_config = types.UploadFileConfig(mime_type=mime_type, name=name)
    remove_duplicate_gemini_audio(name, client)
    return client.files.upload(file=io_obj, config=upload_config)


def transcribe(
    audio: types.File | types.Part,
    client: Client,
    model: str = "gemini-2.5-flash",
    system_prompt: str = "You are a professional transcriber. You output only transcript, no other text.",
    user_prompt: str = "Generate a transcript of the speech",
) -> str:
    """transcribe the audio using Gemini"""
    response = client.models.generate_content(
        model=model,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        contents=[user_prompt, audio],
    )
    return response.text
