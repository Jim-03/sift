from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.websockets import WebSocket

from src.config.database import Session, engine
from src.config.logger import logger
from src.config.socket_manager import SocketManager, SocketManagerDep
from src.routers.job_router import job_router
from src.services.job_service import JobService
from src.services.scraper import search_jobs


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
        uvicorn.run("main:app", host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"Server failed to start: {e}")


# Main instance
app = FastAPI(lifespan=lifespan)
app.include_router(job_router)


# Websocket instant messaging
@app.websocket("/ws")
async def connect(ws: WebSocket, st_manager: SocketManager = SocketManagerDep):
    await st_manager.add_connection(ws)


if __name__ == "__main__":
    bootstrap()
