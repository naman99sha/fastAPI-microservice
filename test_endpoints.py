import shutil
import time
from app.main import app, BASE_DIR, UPLOAD_DIR
from fastapi.testclient import TestClient
from PIL import Image, ImageChops
import io

client = TestClient(app)


def test_get_home():
    response = client.get("/")
    assert response.status_code == 200
    assert 'text/html' in response.headers["content-type"]


def test_post_home():
    response = client.post("/")
    assert response.status_code == 200
    assert 'application/json' in response.headers["content-type"]


def test_echo_upload():
    saved_image_path = BASE_DIR / "images"
    for path in saved_image_path.glob("*"):
        try:
            image = Image.open(path)
        except:
            image = None
        response = client.get("/img-echo/", files={"file": open(path, 'rb')})
        if image is not None:
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            diff = ImageChops.difference(echo_img, image).getbbox()
            assert diff is None
        else:
            assert response.status_code == 400
    # time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)
