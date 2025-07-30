import re
import requests

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


def check_name(name: str):
    """Check availability of original and normalized package names"""
    original_available = name_available(name)
    normalized_name_str = normalize_name(name)
    normalized_available = name_available(normalized_name_str)

    print(f"{name} is {'available' if original_available else 'taken'}")

    if normalized_name_str != name:
        print(
            f"normalized name: {normalized_name_str} is {'available' if normalized_available else 'taken'}"
        )


if __name__ == "__main__":
    # check_name("e-x.a-._m_p-l-e")
    # check_name("requests")
    check_name("handy")
