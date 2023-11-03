from fastapi import APIRouter, Request, Form, status
from ..services.WebScraper import WebScraper
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from celery.result import AsyncResult

router = APIRouter()
web_scraper = WebScraper()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.post("/form")
async def process_form(request: Request, url: str = Form(...)):
    task = web_scraper.scrape_webpage.delay(url)
    return RedirectResponse(url=f"/results/{task.id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/results/{task_id}")
async def get_results(request: Request, task_id: str):
    task = AsyncResult(task_id)
    result = "None"
    if task.successful():
        result = task.result
    return templates.TemplateResponse("results.html", {"request": request, "status": task.status, "result": result})
    # return {'task_id': task_id}