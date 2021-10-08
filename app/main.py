from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Depends,
    File,
    UploadFile
)
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


class Settings(BaseSettings):
    debug: bool = False
    echo_active: bool = False

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


@app.post("/")
def home_detail_view():
    return {"hello": "world"}


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid Endpoint", status=400)
    bytes_str = io.BytesIO(await file.read())
    fname = pathlib.Path(file.filename)
    fext = fname.suffix  # .jpg , .txt
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    # save the file uploaded
    with open(str(dest), 'wb') as out:
        out.write(bytes_str.read())
    return dest
