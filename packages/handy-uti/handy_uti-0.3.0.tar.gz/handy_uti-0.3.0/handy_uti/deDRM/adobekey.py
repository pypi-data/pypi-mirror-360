"""
Retrieve Adobe ADEPT user key.
"""

import xml.etree.ElementTree as etree
from base64 import b64decode
from io import BytesIO

def extract_adobe_key(dat_file: bytes) -> bytes:
    tree = etree.parse(BytesIO(dat_file))
    adeptURL = '{http://ns.adobe.com/adept}'
    expr = f"//{adeptURL}credentials/{adeptURL}privateLicenseKey"
    userkey = tree.findtext(expr)
    decoded_userkey = b64decode(userkey)[26:]
    return decoded_userkey

