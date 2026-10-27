from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect

from src.config.socket_manager import SocketManager, SocketManagerDep


def search_jobs():
    """Scrape jobs from websites"""

    # TODO: Implement job search
    raise RuntimeError("Unimplemented task")


# Schedule to scrape every day between Monday and Friday at 8 AM and 4 PM
scheduler = BackgroundScheduler()
scheduler.add_job(search_jobs, CronTrigger(hour="8, 16", day_of_week="mon-fri"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


# Main instance
app = FastAPI(lifespan=lifespan)


# Websocket instant messaging
@app.websocket("/ws")
async def connect(ws: WebSocket, st_manager: SocketManager = SocketManagerDep):
    await st_manager.add_connection(ws)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
