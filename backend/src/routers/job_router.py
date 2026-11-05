from fastapi import APIRouter, HTTPException
from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session

from src.config.database import DatabaseDep
from src.config.model import JobModel
from src.dto.job_dto import JobDataDto

job_router = APIRouter(prefix="/jobs", tags=["Jobs"])


@job_router.get(
    "", summary="Get jobs", response_model=list[JobDataDto], status_code=200
)
async def get_jobs(
    title: str | None = None,
    company: str | None = None,
    limit: int = 10,
    page: int = 0,
    db: Session = DatabaseDep,
):
    """Retrieve jobs

    Args:
        title: The name of the position to fetch
        company: Company name
        limit: Number of records to fetch in a page
        page: Page number. 0-indexed
        db: Database dependency

    Returns:
        (list[JobDataDto]): List of jobs

    """
    where: ColumnElement[bool] = []

    if company:
        where.append(JobModel.company.ilike(company))
    if title:
        where.append(JobModel.title.ilike(title))
    stmt = (
        db.query(JobModel)
        .order_by(JobModel.created_at)
        .limit(limit)
        .offset(limit * page)
    )

    if where:
        stmt.where(where)

    jobs = stmt.all()

    if len(jobs) == 0:
        raise HTTPException(status_code=404, detail="No jobs at the moment")

    return jobs
