import shutil
import time
from app.main import app, BASE_DIR, UPLOAD_DIR, get_settings
from fastapi.testclient import TestClient
from PIL import Image, ImageChops
import io

client = TestClient(app)


def test_get_home():
    response = client.get("/")
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
        response = client.post("/",
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
        response = client.post("/",
                               files={"file": open(path, 'rb')},
                               headers={
                                   "Authorization": f"JWT {settings.app_auth_token}"}
                               )
        if img is not None:
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2
        else:
            assert response.status_code == 400


def test_echo_upload():
    saved_image_path = BASE_DIR / "images"
    for path in saved_image_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/img-echo/", files={"file": open(path, 'rb')})
        if img is not None:
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            diff = ImageChops.difference(echo_img, img).getbbox()
            assert diff is None
        else:
            assert response.status_code == 400
    # time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)
