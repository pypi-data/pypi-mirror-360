import os
import streamlit as st

sess = st.session_state


def get_api_key(brand: str) -> str | None:
    """Get API key from session state or .env otherwise return None"""
    key_name = f"{brand.upper()}_API_KEY"

    if key_name in sess:
        return sess[key_name]

    if value := os.environ.get(key_name):
        sess[key_name] = value
        return value
    return None


def url_path(title: str) -> str:
    """convert utility title to url path"""
    return title.lower().replace(" ", "_")
