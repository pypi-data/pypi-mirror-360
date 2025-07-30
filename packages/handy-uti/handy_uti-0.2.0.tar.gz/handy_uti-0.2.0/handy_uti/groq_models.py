import pandas as pd
import streamlit as st
from groq import Groq
from pandas import DataFrame
from handy_uti.ui import api_key_input, app_header, main_container

icon = ":material/lightbulb:"
title = "Groq Models"


def model_df(groq_api_key):
    client = Groq(api_key=groq_api_key)

    models = client.models.list()

    data = [model.to_dict() for model in models.data]
    df = DataFrame(data)
    df["created"] = pd.to_datetime(df.created, unit="s").dt.strftime("%Y-%m-%d")
    sorted_df = df[df.active == True].sort_values(
        by=["created", "context_window"], ascending=False
    )[
        [
            "id",
            "created",
            "owned_by",
            "context_window",
            "max_completion_tokens",
        ]
    ]
    # change the column names to be more readable
    sorted_df.columns = [
        "Model ID",
        "Created",
        "Owned By",
        "Context",
        "Output Tokens",
    ]
    return st.dataframe(sorted_df, hide_index=True, use_container_width=True)


def body():
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    with c1:
        groq_api_key = api_key_input("Groq")

    get_models = c2.button(
        "Get Models", use_container_width=True, key="get-groq-models"
    )

    if get_models and not groq_api_key:
        st.error("Please enter a valid Groq API Key")


def app():
    app_header(
        icon=f":orange[{icon}]",
        title=title,
        description="List all currently active and available models in Groq",
    )

    main_container(body)

    if st.session_state.get("get-groq-models"):
        st.write("")
        st.write("")
        st.markdown("#### ✨ &nbsp; Active Models")
        model_df(st.session_state["groq-api-key"])
