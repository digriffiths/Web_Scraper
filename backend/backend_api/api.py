from fastapi import FastAPI
from .routers.web_scraper_router import router as web_scraper_router

app = FastAPI()

app.include_router(web_scraper_router)
