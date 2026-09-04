import asyncio

from src.data import save_urls
from src.dto import Job, Metadata
from src.gemini import Gemini
from src.mail import send_email
from src.ml import get_relevant_jobs
from src.scraper import get_jobs

BATCH = 5
gemini = Gemini()


async def process_job():
    try:
        # Fetch jobs
        jobs = await get_jobs()

        if not jobs:
            return

        # Filter out jobs with higher similarity score
        higher_jobs = get_relevant_jobs(jobs, gemini)

        if not higher_jobs:
            return

        # Extract relevant information
        relevant_data: list[Job] = []

        for i in range(0, len(higher_jobs), BATCH):
            relevant_data.extend(gemini.extract(higher_jobs[i : i + BATCH]).jobs)
        valid_jobs: list[Job] = [job for job in relevant_data if job.is_valid_job]

        # Get job metadata
        metadata: list[Metadata] = []

        for i in range(0, len(valid_jobs), BATCH):
            metadata.extend(gemini.make_notes(valid_jobs[i : i + BATCH]).data)

        if not metadata:
            return

        # Send email
        send_email(valid_jobs, metadata)

        # Save seen urls
        save_urls([job.source_url for job in valid_jobs])
    except Exception as e:
        print(f"An error has occurred: {e}")


if __name__ == "__main__":
    asyncio.run(process_job())
