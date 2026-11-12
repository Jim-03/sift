"""Business logic handling job data"""

import asyncio

from sqlalchemy import insert
from sqlalchemy.orm import Session

from src.config.database import DatabaseDep
from src.config.logger import logger
from src.config.model import JobMetadataModel, JobModel
from src.dto.job_dto import LLMJobDto
from src.services.gemini import GeminiService

DELAY = 60
GEMINI_BATCH_SIZE = 5


class JobService:
    """Business logic handling job data"""

    def __init__(self, db: Session = DatabaseDep):
        self.__db = db
        self.__BATCH_SIZE = 100
        self.gemini = GeminiService()

    def save_jobs(self, jobs: list[LLMJobDto]) -> list[JobModel]:
        """Add new jobs to the database

        Args:
            jobs: List of jobs

        Returns:
            (list[JobModel]): A list of newly saved jobs

        """
        new_jobs = [job.model_dump() for job in jobs]
        saved_jobs = []
        try:
            for i in range(0, len(jobs), self.__BATCH_SIZE):
                batch = []
                for job in new_jobs[i : i + self.__BATCH_SIZE]:
                    values = dict(job)

                    if values.get("deadline") is None:
                        values.pop("deadline")

                    batch.append(values)
                stmt = insert(JobModel).values(batch).returning(JobModel)

                saved_jobs.extend(self.__db.scalars(stmt).all())
            self.__db.commit()

            logger.info(f"Successfully added {len(new_jobs)} new job(s)")

            with open("urls.txt", "a") as f:
                f.write("\n".join(job.url for job in jobs) + "\n")

            return saved_jobs
        except Exception as e:
            logger.error(f"An error has occurred while adding new jobs: {e}")
            raise e

    async def evaluate_jobs(self, jobs: list[JobModel]) -> list[JobMetadataModel]:
        """Assess profile against jobs

        Args:
            jobs: List of new jobs

        Returns:
            (list[JobMatchResult]): A list of assessment

        """
        evaluations = []

        try:
            for i in range(0, len(jobs), GEMINI_BATCH_SIZE):
                tasks = []
                batch = jobs[i : i + GEMINI_BATCH_SIZE]

                for job in batch:
                    tasks.append(self.gemini.evaluate(job.id, job.requirements))

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for res in results:
                    if isinstance(res, Exception):
                        logger.error(f"Task failed with error: {res}")
                    elif isinstance(res, tuple):
                        metadata, job_id = res
                        evaluations.append({"job_id": job_id, **metadata.model_dump()})

                if i + GEMINI_BATCH_SIZE < len(jobs):
                    await asyncio.sleep(DELAY)

            jobs_metadata: list[JobMetadataModel] = []

            for i in range(0, len(evaluations), self.__BATCH_SIZE):
                stmt = (
                    insert(JobMetadataModel)
                    .values(evaluations[i : i + self.__BATCH_SIZE])
                    .returning(JobMetadataModel)
                )
                jobs_metadata.extend(self.__db.scalars(stmt).all())

            self.__db.commit()

            return jobs_metadata
        except Exception:
            raise
