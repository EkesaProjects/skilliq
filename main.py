from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.api import candidate 
import uvicorn

app = FastAPI()

app.include_router(candidate.router, prefix="/candidates", tags=["Candidates"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
# if __name__ == "__main__":
#     uvicorn.run(app, host="175.11.10.98", port=80, reload=True)