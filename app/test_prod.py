import shutil
import time
from app.main import BASE_DIR, UPLOAD_DIR, get_settings
from fastapi.testclient import TestClient
from PIL import Image, ImageChops
import io
import requests

ENPOINT = 'https://fastapi-ms-ocr.herokuapp.com/'


def test_get_home():
    response = requests.get(ENPOINT)
    assert response.status_code == 200
    assert 'text/html' in response.headers["content-type"]


def test_prediction_upload_header_missing():
    saved_image_path = BASE_DIR / "images"
    settings = get_settings()
    for path in saved_image_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = requests.post(ENPOINT,
                                 files={"file": open(path, 'rb')})
        assert response.status_code == 401


def test_prediction_upload():
    saved_image_path = BASE_DIR / "images"
    settings = get_settings()
    for path in saved_image_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = requests.post(ENPOINT,
                                 files={"file": open(path, 'rb')},
                                 headers={
                                     "Authorization": f"JWT {settings.app_auth_token_prod}"}
                                 )
        if img is not None:
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2
        else:
            assert response.status_code == 400
