from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Request,
    Depends,
    File,
    UploadFile
)
import pytesseract
# To return response in terms of HTML strings
from fastapi.responses import HTMLResponse, FileResponse
# For setting up templates in fastAPI
from fastapi.templating import Jinja2Templates
import pathlib  # You can also use OS library
import os
from pydantic import BaseSettings
from functools import lru_cache
import io
import uuid
from PIL import Image


class Settings(BaseSettings):
    debug: bool = False
    echo_active: bool = False
    app_auth_token: str
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


DEBUG = get_settings().debug

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / 'uploads'
templates = Jinja2Templates(directory=str(BASE_DIR/'templates'))


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("home.html", {"request": request})


def verify_auth(authorization=Header(None), settings: Settings = Depends(get_settings)):
    if settings.debug and settings.skip_auth:
        return
    if authorization is None:
        raise HTTPException(detail="Invalid Access", status_code=401)
    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid Access", status_code=401)


@app.post("/")
async def prediction_view(file: UploadFile = File(...), authorization=Header(None), settings: Settings = Depends(get_settings)):
    verify_auth(authorization, settings)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        # If the document uploaded is not an image
        raise HTTPException(detail="Invalid Image", status=400)
    pred = pytesseract.image_to_string(img)
    predictions = [x for x in pred.split('\n')]
    return {"results": predictions, 'original': pred}


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid Endpoint", status=400)
    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        # If the document uploaded is not an image
        raise HTTPException(detail="Invalid Image", status=400)
    fname = pathlib.Path(file.filename)
    fext = fname.suffix  # .jpg , .txt
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    # save the file uploaded
    img.save(dest)
    return dest
