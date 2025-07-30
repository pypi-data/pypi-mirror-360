import json
import streamlit as st
from io import BytesIO
from streamlit.runtime.uploaded_file_manager import UploadedFile
from handy_uti.ui import app_header, main_container
from zipfile import ZIP_DEFLATED, ZipFile

icon = ":material/planet:"
title = "Astrobro Updater"


chinese_locations = {
    "台北": "TW",
    "新北": "TW",
    "基隆": "TW",
    "桃園": "TW",
    "新竹": "TW",
    "苗栗": "TW",
    "台中": "TW",
    "彰化": "TW",
    "雲林": "TW",
    "嘉義": "TW",
    "台南": "TW",
    "高雄": "TW",
    "屏東": "TW",
    "南投": "TW",
    "宜蘭": "TW",
    "花蓮": "TW",
    "台東": "TW",
    "澎湖": "TW",
    "金門": "TW",
    "馬祖": "TW",
    "香港": "HK",
    "澳門": "MO",
    "北京": "CN",
    "上海": "CN",
    "廣州": "CN",
    "深圳": "CN",
}


def modify_city_values(data):
    """Modify city1 and city2 values by appending their country codes."""
    if "city1" in data and data["city1"]:
        city1 = data["city1"]
        if city1 in chinese_locations:
            data["city1"] = f"{city1} - {chinese_locations[city1]}"

    if "city2" in data and data["city2"]:
        city2 = data["city2"]
        if city2 in chinese_locations:
            data["city2"] = f"{city2} - {chinese_locations[city2]}"

    return data


def add_json_to_zip(zip_file: ZipFile, json_file: UploadedFile):
    json_data = json.load(json_file)
    modified_data = modify_city_values(json_data)
    json_str = json.dumps(modified_data, ensure_ascii=False, indent=2)
    zip_file.writestr(json_file.name, json_str)


def download_zip(zip_buffer: BytesIO):
    zip_buffer.seek(0)
    st.download_button(
        label="Download Updated Astrobro Files",
        data=zip_buffer,
        file_name="updated_astrobro_files.zip",
        mime="application/zip",
    )


def main_body():
    json_files = st.file_uploader(
        "Upload AstroBro JSON files",
        type="json",
        accept_multiple_files=True,
    )

    if json_files:
        # Create a BytesIO object to store the zip file
        zip_buffer = BytesIO()

        # Create a zip file
        with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zip_file:
            for json_file in json_files:
                add_json_to_zip(zip_file, json_file)

        # Prepare the zip file for download
        download_zip(zip_buffer)


def app():
    app_header(
        icon=f":orange[{icon}]",
        title=title,
        description="Update [AstroBro](https://hoishing.github.io/astrobro/) JSON files with city names and country codes",
    )
    main_container(body=main_body)


if __name__ == "__main__":
    app()
