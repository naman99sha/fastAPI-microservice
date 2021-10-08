from fastapi import FastAPI, Request, Depends
# To return response in terms of HTML strings
from fastapi.responses import HTMLResponse
# For setting up templates in fastAPI
from fastapi.templating import Jinja2Templates
import pathlib  # You can also use OS library
import os
from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    debug: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


DEBUG = get_settings().debug

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR/'templates'))


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/")
def home_detail_view():
    return {"hello": "world"}
