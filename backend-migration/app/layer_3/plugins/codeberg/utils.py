import tempfile
import os
from scancode.api import get_licenses

def match_license_text(text: str):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(text)
        tmp_path = tmp.name

    try:
        results = get_licenses(tmp_path)
        return results
    finally:
        os.remove(tmp_path)