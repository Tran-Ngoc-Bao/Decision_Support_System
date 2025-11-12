from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["Web"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../../web/template")

templates = Jinja2Templates(directory=TEMPLATE_DIR)

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/compare", response_class=HTMLResponse)
async def read_compare(request: Request, ids: str = ""):
    # Tham số `ids` được nhận từ URL nhưng không cần dùng trong template
    # JavaScript ở client sẽ tự đọc nó từ URL
    return templates.TemplateResponse("compare.html", {"request": request, "ids": ids})


