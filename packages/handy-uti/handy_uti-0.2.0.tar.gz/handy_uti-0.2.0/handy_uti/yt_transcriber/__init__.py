# %% =================================================
import streamlit as st
from .utils import (
    Client,
    YouTube,
    add_punctuation,
    download_yt_audio,
    transcribe,
    upload_gemini_audio,
    youtube_obj,
)
from handy_uti.ui import api_key_input, app_header, divider, main_container

icon = ":material/youtube_activity:"
title = "Youtube Transcriber"


def caption_ui(yt: YouTube | None, langs: list[str], api_key: str) -> None:
    st.markdown("#### 💬 &nbsp; Extract Captions")

    lang = st.selectbox(
        label="Select the language",
        key="caption-lang",
        options=langs,
        index=None,
        format_func=lambda x: x.split(".")[-1],
    )

    format = st.radio(
        label="Select the format",
        key="caption-format",
        options=["srt", "txt", "AI improved txt"],
        index=0,
        horizontal=True,
        disabled=not lang,
    )

    transcript = ""
    if lang:
        if format == "srt":
            transcript = yt.captions[lang].generate_srt_captions()
        elif format == "txt":
            transcript = yt.captions[lang].generate_txt_captions()
        else:
            raw_transcript = yt.captions[lang].generate_txt_captions()
            transcript = add_punctuation(api_key, raw_transcript)

    st.text_area(
        label="Captions",
        key="caption-output",
        value=transcript,
        height=400,
        disabled=not transcript,
    )


def transcribe_ui(yt: YouTube, api_key: str) -> str:
    """Streamlit UI for transcribing audio"""
    st.markdown("#### 🗣️ &nbsp; Transcribe Audio")
    with st.spinner("No captions found, transcribing audio with Gemini..."):
        client = Client(api_key=api_key)
        filename = yt.video_id.lower()
        buffer, mime_type = download_yt_audio(yt)
        audio_file = upload_gemini_audio(filename, buffer, mime_type, client)

        transcript = transcribe(audio_file, client)
        st.text_area(
            label="Transcript", key="transcript-output", value=transcript, height=400
        )


def confirm_transcribe(yt, api_key):
    st.info("No captions found, transcribing audio with Gemini?")
    if st.button("Confirm Transcribe", key="confirm-transcribe"):
        transcribe_ui(yt, api_key)


# %% ================================================= streamlit app


def body():
    api_key = api_key_input("Gemini")
    url = st.text_input("Youtube URL", key="url-input", disabled=not api_key)

    if not api_key or not url:
        st.stop()

    if not (yt := youtube_obj(url)):
        st.error("Invalid URL")
        st.stop()

    langs = [c.code for c in yt.captions]

    divider(key=1)

    if langs or not yt:
        caption_ui(yt, langs, api_key)
    else:
        confirm_transcribe(yt, api_key)


def app():
    app_header(
        icon=f":red[{icon}]",
        title=title,
        description="Extract captions if available, transcribe the audio with AI otherwise",
    )

    main_container(body)


# %% ================================================= test

if __name__ == "__main__":
    yt = youtube_obj("https://www.youtube.com/live/o8NiE3XMPrM?si=jf-nq03VX72pW--9")
    langs = [c.code for c in yt.captions] if yt else []

    if langs or not yt:
        print("caption_ui")
    else:
        print("transcribe_ui")

# %%
