from handy_uti.deDRM import extract_adobe_key
from pathlib import Path


def test_extract_adobe_key():
    # Test fixtures are in the assets directory
    sample_dat_file = Path("tests/assets/dummy-activation.dat")
    expected_key_file = Path("tests/assets/dummy-adobekey.der")

    with open(sample_dat_file, "rb") as f:
        dat_content = f.read()

    result = extract_adobe_key(dat_content)

    # Compare the result with the expected key file
    with open(expected_key_file, "rb") as f:
        expected_key = f.read()

    assert result == expected_key, "Extracted key does not match the expected key"
