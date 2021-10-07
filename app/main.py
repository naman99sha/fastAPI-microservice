from fastapi import FastAPI, Request
# To return response in terms of HTML strings
from fastapi.responses import HTMLResponse
# For setting up templates in fastAPI
from fastapi.templating import Jinja2Templates
import pathlib  # You can also use OS library

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR/'templates'))


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request):
    print(request)
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/")
def home_detail_view():
    return {"hello": "world"}
