# %% =================================================
import io
import mimetypes
import pypandoc
import streamlit as st
from bs4 import BeautifulSoup
from ebooklib.epub import (
    EpubBook,
    EpubHtml,
    EpubItem,
    EpubNav,
    EpubNcx,
    Link,
    write_epub,
)
from pathlib import Path
from streamlit.runtime.uploaded_file_manager import UploadedFile
from handy_uti.ui import app_header, divider, main_container
from zipfile import ZipFile

icon = ":material/markdown:"
title = "MD to Epub"


# %% ================================================= extract files from zip


def unzip_file(zip_file: UploadedFile) -> dict[str, bytes]:
    """Unzip the uploaded file-like object and return a dictionary of file bytes"""
    file_bytes = {}
    with ZipFile(zip_file) as zf:
        for filename in zf.namelist():
            file_bytes[filename] = zf.read(filename)
    return file_bytes


def xhtml_content(file_bytes: dict[str, bytes]) -> str:
    """extract the markdown and convert to html with header ids for anchor links"""
    md_filename = next((n for n in file_bytes if n.lower().endswith(".md")), None)
    md = file_bytes[md_filename].decode("utf-8")

    # convert markdown+math to HTML with embedded MathML
    html = pypandoc.convert_text(
        md, to="html", format="md", extra_args=["--mathml", "--standalone"]
    )
    return html


# %% ================================================= epub processing


def create_epub(name: str):
    """create a new epub object"""
    book = EpubBook()
    book.set_identifier("id123456")
    book.set_title(name)
    book.add_author("Unknown")
    return book


def add_chapter(book: EpubBook, xhtml: str):
    """add the main content to the book inplace"""
    html = EpubHtml(
        title="Main",
        file_name="main.xhtml",
        content=xhtml,
        media_type="application/xhtml+xml",
    )
    book.add_item(html)
    book.spine = ["nav", html]


def add_toc(book: EpubBook, xhtml: str):
    """add a flat TOC from h1 headings to the book inplace"""
    soup = BeautifulSoup(xhtml, "lxml")
    toc_links = []
    for h1 in soup.find_all("h1"):
        heading_text = h1.get_text(strip=True)
        heading_id = h1.get("id")
        if heading_id:
            toc_links.append(Link(f"main.xhtml#{heading_id}", heading_text, heading_id))
    if toc_links:
        book.toc = tuple(toc_links)
    else:
        book.toc = (Link("main.xhtml", "Main", "main"),)
    # add navigation files, required for epub2 and epub3
    book.add_item(EpubNcx())
    book.add_item(EpubNav())


def add_images(book: EpubBook, content_bytes: dict[str, bytes]):
    """add the images to the book inplace"""
    for filepath, content in content_bytes.items():
        mime, _ = mimetypes.guess_type(filepath)
        if mime and mime.startswith("image"):
            filename = Path(filepath).name
            # filter hidden files created by ZipFile lib
            if not filename.startswith("."):
                img_item = EpubItem(
                    uid=filename,
                    file_name=filename,
                    media_type=mime,
                    content=content,
                )
                book.add_item(img_item)


# %% ================================================= streamlit UI


def body():
    st.markdown(
        """
        #### 🧑‍💻 Usage

        - Upload the zip file created in [Mistral OCR](/mistral_ocr)

        OR

        - Put a markdown file with images in the same folder.
        - Zip the folder, name the zip file as the title of the epub.
        - Upload the zip file.
        - Download the epub with TOC generated from all H1 headings.
        """
    )
    divider()

    zip_file = st.file_uploader(
        label="Upload zipped markdown + images",
        type="zip",
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    if not zip_file:
        return

    with st.spinner("Processing..."):
        file_bytes_dict = unzip_file(zip_file)

        epub = create_epub(Path(zip_file.name).stem)
        xhtml = xhtml_content(file_bytes_dict)
        add_images(epub, file_bytes_dict)
        add_chapter(epub, xhtml)
        add_toc(epub, xhtml)

        epub_io = io.BytesIO()
        write_epub(epub_io, epub)
        epub_io.seek(0)

        st.download_button(
            label="Download EPUB",
            data=epub_io,
            file_name=Path(zip_file.name).with_suffix(".epub").name,
            mime="application/epub+zip",
            on_click="ignore",
            icon=":material/download:",
        )


def app():
    app_header(
        icon=f":violet[{icon}]",
        title=title,
        description="Convert markdown with images to epub",
    )
    main_container(body)


# %% ================================================= testing

if __name__ == "__main__":
    app()


# %% ================================================= trail

# from pathlib import Path
# from streamlit.proto.Common_pb2 import FileURLs
# from streamlit.runtime.uploaded_file_manager import UploadedFile, UploadedFileRec

# uploaded_file = UploadedFile(
#     record=UploadedFileRec(
#         file_id="123",
#         name="raw.zip",
#         type="application/zip",
#         data=Path("raw.zip").read_bytes(),
#     ),
#     file_urls=FileURLs(
#         upload_url="https://example.com/upload",
#         delete_url="https://example.com/delete",
#     ),
# )

# content_bytes = unzip_file(uploaded_file)

# html = xhtml_content(content_bytes)
# Path("test.html").write_text(html)


# epub = create_epub(Path(uploaded_file.name).stem)
# add_images(epub, content_bytes)
# add_chapter(epub, html)
# add_toc(epub, html)


# epub_io = io.BytesIO()
# write_epub(epub_io, epub)
# epub_io.seek(0)

# Path("test.epub").write_bytes(epub_io.getbuffer())
