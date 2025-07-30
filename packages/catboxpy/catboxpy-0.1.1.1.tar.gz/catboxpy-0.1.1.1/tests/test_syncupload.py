import os
import pytest
from catboxpy import CatboxClient

client  = CatboxClient()

def test_upload_url():
    url = client.upload('https://docs.pytest.org/en/stable/_static/pytest1.png')
    assert url.startswith('https://files.catbox.moe/')


@pytest.mark.skipif(not os.path.exists("tests/test.png"), reason="Local file not found")
def test_upload_file():
    url = client.upload("tests/example.jpg")
    assert url.startswith("https://files.catbox.moe/")