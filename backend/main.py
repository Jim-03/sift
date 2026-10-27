from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI


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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
