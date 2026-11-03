"""Business logic handling job data"""

from sqlalchemy import insert
from sqlalchemy.orm import Session

from src.config.database import DatabaseDep
from src.config.logger import logger
from src.config.model import JobModel
from src.dto.job_dto import LLMJobDto


class JobService:
    """Business logic handling job data"""

    def __init__(self, db: Session = DatabaseDep):
        self.__db = db
        self.__BATCH_SIZE = 100

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
                stmt = (
                    insert(JobModel)
                    .values(new_jobs[i : i + self.__BATCH_SIZE])
                    .returning(JobModel)
                )

                saved_jobs.extend(self.__db.scalars(stmt).all())
            self.__db.commit()

            logger.info(f"Successfully added {len(new_jobs)} new job(s)")

            return saved_jobs
        except Exception as e:
            logger.error(f"An error has occurred while adding new jobs: {e}")
            raise e
