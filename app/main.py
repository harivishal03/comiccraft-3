"""ComicCraft FastAPI entry point.  Run:  uvicorn app.main:app --reload"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.routes import router

app = FastAPI(title="ComicCraft - AI Comic Story Creator")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(router)
