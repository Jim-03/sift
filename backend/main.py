import os
import secrets
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.websockets import WebSocket
from starlette.responses import JSONResponse

from src.config.database import Session, engine
from src.config.logger import logger
from src.config.socket_manager import SocketManager, SocketManagerDep
from src.routers.job_router import job_router
from src.services.job_service import JobService
from src.services.scraper import search_jobs

load_dotenv()

AUTHENTICATION_KEY = os.getenv("AUTHENTICATION_KEY", "replace_me")
PROFILE = os.getenv("PROFILE", "development")
PUBLIC_DEV_PATHS = {
    "/docs",
    "/openapi.json",
    "/redoc",
}


async def process_jobs():
    """Scrape jobs from websites"""
    session = Session()
    job_service = JobService(session)
    # socket_manager = SocketManager()
    jobs = await search_jobs()

    if len(jobs) != 0:
        try:
            job_service.save_jobs(jobs)
            # TODO: Notify client devices
        finally:
            session.close()


# Schedule to scrape every day between Monday and Friday at 8 AM and 4 PM
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(process_jobs, CronTrigger(hour="8, 16", day_of_week="mon-fri"))
    scheduler.start()
    yield
    scheduler.shutdown()


def bootstrap():
    """Check database availability and launch the app"""
    try:
        with engine.connect():
            logger.info("Connected to the database")
        uvicorn.run(
            "main:app", host="0.0.0.0", port=8080, reload=PROFILE == "development"
        )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")


# Main instance
app = FastAPI(lifespan=lifespan)
app.include_router(job_router)


# WebSocket instant messaging
@app.websocket("/ws")
async def connect(ws: WebSocket, st_manager: SocketManager = SocketManagerDep):
    await st_manager.add_connection(ws)


# Security
@app.middleware("http")
async def authenticate_token(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    if PROFILE == "development" and request.url.path in PUBLIC_DEV_PATHS:
        return await call_next(request)
    auth_header = request.headers.get("Authorization")

    if auth_header is None or not auth_header.startswith("Bearer "):
        logger.warn("Unauthorized request")
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    token = auth_header[7:]

    if not secrets.compare_digest(token, AUTHENTICATION_KEY):
        logger.warn("Unauthorized request")
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    response = await call_next(request)
    return response


if __name__ == "__main__":
    bootstrap()
