from http.client import HTTPException

from fastapi import FastAPI, Depends, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict


from .middleware.default import setup_middlewares
from .routers import locations, search, item, dss, web


app = FastAPI(title="House Rental API", version="1.0.0")

# middle ware
setup_middlewares(app)

# static file
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/template")

# routers + prefix + tags

app.include_router(locations.router, prefix="/api", tags=["Locations"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(item.router, prefix="/api", tags=["Items"])
app.include_router(dss.router, prefix="/api", tags=["DSS"])
app.include_router(web.router, prefix="", tags=["Web"])
