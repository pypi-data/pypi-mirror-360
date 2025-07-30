import re
import requests
import streamlit as st
from handy_uti.ui import app_header, divider, main_container

icon = ":material/check_circle:"
title = "PyPi Name Checker"

BASE_URL = "https://pypi.org/pypi"


def name_available(name: str) -> bool:
    """Request response from PyPi API"""
    target_url = f"{BASE_URL}/{name}/json"
    response = requests.get(target_url)
    result = response.json()
    return result.get("message") == "Not Found"


def normalize_name(name: str) -> str:
    """Normalize package name by replacing common substitutions and removing separators"""
    name = name.replace("0", "o").replace("1", "l")
    name = re.sub(r"[._-]", "", name)  # remove ., _, -
    return name.lower()


def check_name(name: str) -> dict[str, bool]:
    """Check availability of original and normalized package names"""
    normalized_name_str = normalize_name(name)
    output = {
        name: name_available(name),
    }

    if normalized_name_str != name:
        key = f"{normalized_name_str} (normalized)"
        output |= {key: name_available(normalized_name_str)}

    return output


def body():
    st.markdown(
        """
        ##### ✅ &nbsp; Availability Check

        - check if the package name is available on PyPi

        ##### ⚠️ &nbsp; Similarity Check

        - PyPi will [normalize](https://stackoverflow.com/a/71490005/264382) the package name and check if its taken by existing packages
        - package with taken normalized name cannot be registered
        """,
    )
    divider()
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    c1.text_input("Package Names", key="names", placeholder="name1, name2, name3...")
    if c2.button("Check", use_container_width=True):
        # divider(key="divider2")
        st.write("")
        names = st.session_state.names.split(",")
        for name in names:
            for key, value in check_name(name.strip()).items():
                badge = (
                    ":green-badge[:material/check_circle: available]"
                    if value
                    else ":red-badge[:material/do_not_disturb_on: taken]"
                )
                st.write(f"&nbsp; {badge} &nbsp; {key}")


def app():
    app_header(
        icon=f":blue[{icon}]",
        title=title,
        description="Check the availability of PyPi package names",
    )

    main_container(body)
