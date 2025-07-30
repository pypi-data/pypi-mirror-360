# %% =================================================
import streamlit as st
from base64 import b64decode
from io import BytesIO
from mistralai import Mistral, OCRResponse
from pathlib import Path
from streamlit.elements.widgets.file_uploader import UploadedFile
from handy_uti.ui import api_key_input, app_header, divider, main_container
from zipfile import ZIP_DEFLATED, ZipFile

model = "mistral-ocr-latest"
icon = ":material/scanner:"
title = "Mistral OCR"


# %% ================================================= ocr functions


def ocr(client: Mistral, url: str, is_pdf: bool) -> OCRResponse:
    """OCR a PDF or image URL and return the Mistral OCR response"""
    doc_type = "document_url" if is_pdf else "image_url"
    return client.ocr.process(
        model=model,
        document={"type": doc_type, doc_type: url},
        include_image_base64=True,
    )


# %% ================================================= file preparation


def upload_file_to_mistral(client: Mistral, st_file: UploadedFile) -> str:
    """Upload a streamlit uploaded file to Mistral and return the file ID"""
    uploaded_file = client.files.upload(
        file={
            "file_name": st_file.name,
            "content": st_file.getvalue(),
        },
        purpose="ocr",
    )
    return uploaded_file.id


# %% ================================================= process response


def extract_markdown(response: OCRResponse) -> str:
    """Extract markdown from OCR response"""
    markdown_parts = []
    for page in response.pages:
        markdown_parts.append(page.markdown)

    return "\n\n".join(markdown_parts)


def extract_images(response: OCRResponse) -> dict[str, str]:
    """Extract base64 data from OCR response"""
    images = {}
    for page in response.pages:
        for img in page.images:
            # img.id is the same as the image name
            images[img.id] = img.image_base64

    return images


# %% ================================================= create zip buffer


def create_zip(markdown: str, images: dict[str, str]) -> BytesIO:
    """Create a zip file from markdown and images {name: base64_string} and return a zip buffer"""
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zip_file:
        # Add markdown file
        zip_file.writestr("content.md", markdown)

        # Add images
        for img_name, img_base64 in images.items():
            # Decode base64 to binary
            base64_data = img_base64.split(",")[1]
            img_binary = b64decode(base64_data)

            # Add image to zip
            zip_file.writestr(img_name, img_binary)

    # Reset buffer position to the beginning
    zip_buffer.seek(0)
    return zip_buffer


# %% =================================================  streamlit app


def body():
    api_key = api_key_input("mistral")

    divider()

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["pdf", "jpg", "png"],
        disabled=not api_key,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

    if not uploaded_file:
        return

    client = Mistral(api_key=api_key)
    with st.status("Processing...", expanded=True) as status:
        for st_file in uploaded_file:
            is_pdf = "pdf" in st_file.type
            file_id = upload_file_to_mistral(client, st_file)
            signed_url = client.files.get_signed_url(file_id=file_id)
            ocr_response = ocr(client, signed_url.url, is_pdf=is_pdf)
            markdown = extract_markdown(ocr_response)
            images = extract_images(ocr_response)
            zip_buffer = create_zip(markdown, images)
            zip_filename = Path(st_file.name).with_suffix(".zip")
            st.download_button(
                label=f"Download: {zip_filename}",
                data=zip_buffer,
                file_name=str(zip_filename),
                icon=":material/download:",
                mime="application/zip",
                type="tertiary",
                on_click="ignore",
            )
        status.update(label="OCR Completed", state="complete")


def app():
    app_header(
        icon=f":orange[{icon}]",
        title=title,
        description="Turn PDF or Image to Markdown with Mistral AI OCR",
    )
    main_container(body)


# %% ================================================= for testing


if __name__ == "__main__":
    app()
